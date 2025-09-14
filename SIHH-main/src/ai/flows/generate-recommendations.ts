
'use server';

/**
 * @fileOverview Recommendation AI agent for Railway Decision Support.
 *
 * - generateRecommendations - A function that generates action recommendations based on current disruptions and train statuses to minimize delays.
 * - GenerateRecommendationsInput - The input type for the generateRecommendations function.
 * - GenerateRecommendationsOutput - The return type for the generateRecommendations function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateRecommendationsInputSchema = z.object({
  disruptions: z
    .array(z.string())
    .describe('A list of current disruptions affecting the rail network.'),
  trainStatuses: z
    .array(z.string())
    .describe('A list of current train statuses (on-time, delayed, at risk).'),
});
export type GenerateRecommendationsInput = z.infer<typeof GenerateRecommendationsInputSchema>;


const RecommendationSchema = z.object({
  recommendation: z.string().describe('A clear, actionable recommendation for the railway controller.'),
  reason: z.string().describe('A concise explanation for why the recommendation is being made.'),
  confidence: z.number().int().min(0).max(100).describe('A confidence score (0-100) for the recommendation.'),
  impact: z.enum(['Low', 'Medium', 'High']).describe('The estimated impact of implementing this recommendation.'),
  timeSaving: z.number().int().describe('Estimated time saved in minutes for the affected trains.'),
  performanceImprovement: z.number().describe('Projected percentage improvement in overall network punctuality.'),
});


const GenerateRecommendationsOutputSchema = z.object({
  update: z.string().describe('A brief summary of the most critical issue affecting the network.'),
  recommendations: z.array(RecommendationSchema),
});
export type GenerateRecommendationsOutput = z.infer<typeof GenerateRecommendationsOutputSchema>;

export async function generateRecommendations(
  input: GenerateRecommendationsInput
): Promise<GenerateRecommendationsOutput> {
  // Mock implementation - provides realistic recommendations without API key
  return generateMockRecommendations(input);
}

// Mock AI function that provides realistic railway management recommendations
function generateMockRecommendations(input: GenerateRecommendationsInput): GenerateRecommendationsOutput {
  const { disruptions, trainStatuses } = input;
  
  // Analyze disruptions to determine critical issues
  const hasSignalFailure = disruptions.some(d => d.toLowerCase().includes('signal'));
  const hasTrackBlockage = disruptions.some(d => d.toLowerCase().includes('track') || d.toLowerCase().includes('blockage'));
  const hasDelay = trainStatuses.some(s => s.toLowerCase().includes('delayed'));
  const hasAtRisk = trainStatuses.some(s => s.toLowerCase().includes('at risk'));
  
  // Generate contextual recommendations based on current situation
  let update = "Network operating normally";
  let recommendations = [];
  
  if (hasSignalFailure) {
    update = "Critical signal failure detected at Ghaziabad junction affecting multiple routes";
    recommendations = [
      {
        recommendation: "Implement manual signaling protocol and deploy RRI team to affected section",
        reason: "Manual signaling will restore basic operations while technical team resolves the failure",
        confidence: 95,
        impact: "High" as const,
        timeSaving: 45,
        performanceImprovement: 12.5
      },
      {
        recommendation: "Divert express trains via alternative routes (Tundla-Agra loop)",
        reason: "Reduces congestion at affected junction and maintains service continuity",
        confidence: 88,
        impact: "Medium" as const,
        timeSaving: 30,
        performanceImprovement: 8.2
      },
      {
        recommendation: "Prioritize passenger trains over freight services for next 2 hours",
        reason: "Minimizes passenger inconvenience during peak travel hours",
        confidence: 92,
        impact: "Medium" as const,
        timeSaving: 25,
        performanceImprovement: 6.8
      }
    ];
  } else if (hasTrackBlockage) {
    update = "Track blockage reported on main line affecting freight operations";
    recommendations = [
      {
        recommendation: "Deploy track maintenance team with heavy machinery to clear debris",
        reason: "Immediate clearance will restore full line capacity and prevent further delays",
        confidence: 90,
        impact: "High" as const,
        timeSaving: 60,
        performanceImprovement: 15.3
      },
      {
        recommendation: "Reroute affected freight trains via secondary lines",
        reason: "Maintains cargo delivery schedules while main line is being cleared",
        confidence: 85,
        impact: "Medium" as const,
        timeSaving: 40,
        performanceImprovement: 10.1
      }
    ];
  } else if (hasDelay || hasAtRisk) {
    update = "Multiple trains experiencing delays due to operational constraints";
    recommendations = [
      {
        recommendation: "Implement dynamic scheduling adjustments for next 3 hours",
        reason: "Proactive rescheduling prevents cascading delays across the network",
        confidence: 87,
        impact: "Medium" as const,
        timeSaving: 35,
        performanceImprovement: 9.4
      },
      {
        recommendation: "Increase platform dwell time at major stations by 2-3 minutes",
        reason: "Reduces pressure on train crews and improves passenger boarding efficiency",
        confidence: 82,
        impact: "Low" as const,
        timeSaving: 15,
        performanceImprovement: 4.2
      },
      {
        recommendation: "Coordinate with station masters to optimize train sequencing",
        reason: "Better coordination reduces conflicts and improves overall punctuality",
        confidence: 89,
        impact: "Medium" as const,
        timeSaving: 28,
        performanceImprovement: 7.6
      }
    ];
  } else {
    // Normal operations - provide proactive recommendations
    update = "Network operating smoothly with minor optimization opportunities";
    recommendations = [
      {
        recommendation: "Implement predictive maintenance for signal systems at high-traffic junctions",
        reason: "Prevents unexpected failures during peak hours and improves reliability",
        confidence: 91,
        impact: "Low" as const,
        timeSaving: 20,
        performanceImprovement: 3.8
      },
      {
        recommendation: "Optimize freight train scheduling to reduce passenger train conflicts",
        reason: "Better separation of freight and passenger services improves overall efficiency",
        confidence: 86,
        impact: "Low" as const,
        timeSaving: 12,
        performanceImprovement: 2.9
      }
    ];
  }
  
  return {
    update,
    recommendations
  };
}

const prompt = ai.definePrompt({
  name: 'generateRecommendationsPrompt',
  input: {schema: GenerateRecommendationsInputSchema},
  output: {schema: GenerateRecommendationsOutputSchema},
  prompt: `You are an expert AI decision support assistant for Indian Railways controllers. Your task is to provide clear, actionable recommendations to manage network disruptions and maintain punctuality.

  Analyze the following data from the North-Central railway network:

  Current Disruptions:
  {{#each disruptions}}- {{this}}\n{{/each}}

  Current Train Statuses:
  {{#each trainStatuses}}- {{this}}\n{{/each}}

  Based on the provided data, generate a response object. This object must contain:
  1. A single 'update' field: A very brief summary of the most critical issue (e.g., "Major signaling failure at Ghaziabad").
  2. A 'recommendations' array: This array should contain 2-3 distinct, high-priority recommendations to mitigate the disruptions. Each recommendation in the array must be a JSON object with the following structure:
     - "recommendation": A specific, actionable instruction (e.g., "Divert New Delhi-bound trains from Tundla via Agra loop").
     - "reason": A short explanation for the action (e.g., "Minimizes delay for 5 express services and avoids a major bottleneck.").
     - "confidence": Your confidence level in this recommendation (integer, 0-100).
     - "impact": The potential impact of the issue if not addressed ('Low', 'Medium', or 'High').
     - "timeSaving": Estimated total minutes saved across all affected trains.
     - "performanceImprovement": Estimated punctuality gain for the network as a percentage.
  `,
});

const generateRecommendationsFlow = ai.defineFlow(
  {
    name: 'generateRecommendationsFlow',
    inputSchema: GenerateRecommendationsInputSchema,
    outputSchema: GenerateRecommendationsOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
