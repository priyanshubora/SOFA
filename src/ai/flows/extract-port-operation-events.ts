'use server';
/**
 * @fileOverview This file defines a Genkit flow for extracting port operation events from Statements of Fact (SoFs).
 * It also calculates laytime and summarizes the events in a single operation.
 *
 * - extractPortOperationEvents - A function that takes the content of an SoF and returns structured data, laytime calculations, and a summary.
 * - ExtractPortOperationEventsInput - The input type for the extractPortOperationEvents function.
 * - ExtractPortOperationEventsOutput - The return type for the extractPortOperationEvents function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'zod';

const ExtractPortOperationEventsInputSchema = z.object({
  sofContent: z.string().describe("The text content of the Statement of Fact file."),
});
export type ExtractPortOperationEventsInput = z.infer<typeof ExtractPortOperationEventsInputSchema>;

const LaytimeCalculationSchema = z.object({
  totalLaytime: z.string().describe('The total calculated laytime in a human-readable format (e.g., "2 days, 4 hours, 30 minutes").'),
  allowedLaytime: z.string().describe('The standard allowed laytime based on contract (default or specified).'),
  timeSaved: z.string().describe('Time saved if operations finished before allowed laytime expired.'),
  demurrage: z.string().describe('Extra time taken beyond the allowed laytime.'),
  demurrageCost: z.string().optional().describe('The calculated cost of demurrage based on the extra time taken and a standard daily rate (e.g., "$20,000").'),
  laytimeEvents: z.array(z.object({
    event: z.string(),
    startTime: z.string().describe('The start time of the event in YYYY-MM-DD HH:MM format.'),
    endTime: z.string().describe('The end time of the event in YYYY-MM-DD HH:MM format.'),
    duration: z.string(),
    isCounted: z.boolean().describe('Whether this event duration counts towards the total laytime.'),
    reason: z.string().optional().describe('Reason why the event is or is not counted towards laytime.'),
  })).describe('A breakdown of each event and whether it contributed to the laytime.'),
});
export type LaytimeCalculation = z.infer<typeof LaytimeCalculationSchema>;

const SubEventSchema = z.object({
    event: z.string(),
    category: z.string(),
    startTime: z.string(),
    endTime: z.string(),
    duration: z.string(),
    status: z.string(),
    remark: z.string().optional(),
});

const TimelineBlockSchema = z.object({
    name: z.string(),
    category: z.string(),
    time: z.tuple([z.number(), z.number()]),
    duration: z.string(),
    startTime: z.string(),
    endTime: z.string(),
    subEvents: z.array(SubEventSchema),
}).describe("A block of merged, overlapping events for timeline visualization.");
export type TimelineBlock = z.infer<typeof TimelineBlockSchema>;

const ExtractPortOperationEventsOutputSchema = z.object({
  vesselName: z.string().describe("The name of the vessel (or ship) mentioned in the SoF. Look for 'Vessel Name' or 'Ship Name'."),
  portOfCall: z.string().optional().describe("The port where the operations are taking place."),
  berth: z.string().optional().describe("The specific berth or anchorage location."),
  cargoDescription: z.string().optional().describe("Description of the cargo being loaded or discharged."),
  cargoQuantity: z.string().optional().describe("The quantity of the cargo (e.g., in metric tons)."),
  voyageNumber: z.string().optional().describe("The voyage number of the vessel."),
  noticeOfReadinessTendered: z.string().optional().describe("The date and time when the Notice of Readiness (NOR) was tendered."),
  events: z.array(
    z.object({
      event: z.string().describe('The exact, verbatim text for the port operation event from the remarks column (e.g., "Pilot Attended On Board in the vessel"). Do not summarize or change it.'),
      category: z.string().describe("The general category of the event (e.g., 'Arrival', 'Cargo Operations', 'Departure', 'Delays', 'Stoppages', 'Bunkering', 'Anchorage', or 'Other')."),
      startTime: z.string().describe('The start time of the event in YYYY-MM-DD HH:MM format.'),
      endTime: z.string().describe('The end time of the event in YYYY-MM-DD HH:MM format.'),
      duration: z.string().describe('The calculated duration of the event (e.g., "2h 30m").'),
      status: z.string().describe("The status of the event (e.g., 'Completed', 'In Progress', 'Delayed')."),
      remark: z.string().optional().describe('Any additional notes, comments or details about the event from the SoF.')
    })
  ).describe('An array of port operation events with their start and end times, sorted chronologically.'),
  timelineBlocks: z.array(TimelineBlockSchema).optional().describe("An array of merged, overlapping event blocks for timeline visualization."),
  laytimeCalculation: LaytimeCalculationSchema.optional().describe('The detailed laytime calculation results.'),
  eventsSummary: z.string().optional().describe('A concise, bulleted summary of the key insights from the port events.'),
});
export type ExtractPortOperationEventsOutput = z.infer<typeof ExtractPortOperationEventsOutputSchema>;

export async function extractPortOperationEvents(input: ExtractPortOperationEventsInput): Promise<ExtractPortOperationEventsOutput> {
  return extractPortOperationEventsFlow(input);
}

const extractPortOperationEventsPrompt = ai.definePrompt({
  name: 'extractPortOperationEventsPrompt',
  input: {schema: ExtractPortOperationEventsInputSchema},
  output: {schema: ExtractPortOperationEventsOutputSchema.omit({ timelineBlocks: true })},
  prompt: `You are an expert maritime logistics AI with exceptional attention to detail. Your task is to analyze the provided Statement of Fact (SoF) and perform three tasks with the highest level of accuracy and completeness.

Primary Directive:
You must not miss ANY event. Every line item in the Statement of Facts (SoF) that contains a timestamp must be extracted as a unique event.

1. Event Extraction (Line-by-Line)

Parse the SoF line-by-line.

If a row has a date and/or time, it is an event.

For each event, extract the following fields into JSON:

{
  "event": "Verbatim text from Remarks column (do not summarize)",
  "category": "One of ['Arrival', 'Cargo Operations', 'Departure', 'Delays', 'Stoppages', 'Bunkering', 'Anchorage', 'Other']",
  "startTime": "YYYY-MM-DD HH:MM",
  "endTime": "YYYY-MM-DD HH:MM (or same as startTime if point-in-time event)",
  "duration": "e.g., '2h 30m', '15m', or '0m' if same start/end",
  "status": "e.g., 'Completed', 'In Progress', 'Delayed', or 'Not Mentioned' if unavailable",
  "remark": "Any additional text from the Remarks column for this event"
}


If a field is missing in the SoF, do not crash. Just use "Not Mentioned" or leave it empty.

The only mandatory fields are:

vesselName

events

If these two cannot be extracted → return:

{"error": "Unable to extract vessel name and events"}

2. Master Details Extraction

Also extract these if present in the SoF (if missing, still proceed):

vesselName (Ship Name)

portOfCall (and berth/anchorage if mentioned)

voyageNumber

cargoDescription and cargoQuantity

noticeOfReadinessTendered (date/time)

3. Laytime Calculation

Assume standard allowed laytime = 3 days (72h) unless otherwise stated.

Create a laytimeEvents array where each event includes:

{
  "event": "Verbatim event text",
  "duration": "e.g., 2h 30m",
  "countedTowardsLaytime": true/false,
  "reason": "Explain why this event counts or not (e.g., 'Cargo ops count', 'Rain delay excluded')"
}


Then calculate:

totalLaytime (hours/minutes)

timeSaved (despatch) if laytime < 72h

demurrage if laytime > 72h

demurrageCost (standard $20,000/day, prorated)

4. Summary (Insights)

Generate a short, bullet-point summary with:

Total time spent in port

Total time spent on cargo operations

Total time lost to delays/stoppages (with reasons)

5. Output Format

Final output must always be in valid JSON with this structure:

{
  "vesselName": "...",
  "portOfCall": "...",
  "voyageNumber": "...",
  "cargoDescription": "...",
  "cargoQuantity": "...",
  "noticeOfReadinessTendered": "...",
  "events": [...chronologically sorted list of events...],
  "laytimeEvents": [...],
  "totalLaytime": "...",
  "timeSaved": "...",
  "demurrage": "...",
  "demurrageCost": "...",
  "summary": [
    "Insight 1",
    "Insight 2",
    "Insight 3"
  ]
}


📌 Key Rules Recap

Never skip events.

Always preserve verbatim event text.

Handle missing fields gracefully.

Only vesselName and events are mandatory.

Always output valid JSON.
SoF Content:
{{{sofContent}}}`,
});

const extractPortOperationEventsFlow = ai.defineFlow(
  {
    name: 'extractPortOperationEventsFlow',
    inputSchema: ExtractPortOperationEventsInputSchema,
    outputSchema: ExtractPortOperationEventsOutputSchema,
  },
  async input => {
    const {output} = await extractPortOperationEventsPrompt(input);
    // The AI is not responsible for creating timeline blocks, so we can return the output as is.
    // The frontend will handle the creation of timeline blocks.
    return output as ExtractPortOperationEventsOutput;
  }
);
