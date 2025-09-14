/**
 * @fileOverview A flow for generating explanatory videos for railway disruptions.
 *
 * - generateVideo - A function that generates a video based on a text prompt.
 * - GenerateVideoInput - The input type for the generateVideo function.
 * - GenerateVideoOutput - The return type for the generateVideo function.
 */
'use server';

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { googleAI } from '@genkit-ai/googleai';

const GenerateVideoInputSchema = z.object({
  prompt: z.string().describe('The text prompt to generate the video from.'),
});
export type GenerateVideoInput = z.infer<typeof GenerateVideoInputSchema>;

const GenerateVideoOutputSchema = z.object({
  videoUrl: z.string().describe('The data URI of the generated video.'),
});
export type GenerateVideoOutput = z.infer<typeof GenerateVideoOutputSchema>;

// The core flow definition using Genkit
const generateVideoFlow = ai.defineFlow(
  {
    name: 'generateVideoFlow',
    inputSchema: GenerateVideoInputSchema,
    outputSchema: GenerateVideoOutputSchema,
  },
  async ({ prompt }) => {
    console.log('Starting video generation for prompt:', prompt);
    let { operation } = await ai.generate({
      model: googleAI.model('veo-2.0-generate-001'),
      prompt: `Create a short, informative video, in the style of a UK railway training video, that visually explains the concept of: "${prompt}". Use simple graphics and text overlays. The video should be clear and concise for a railway controller.`,
      config: {
        durationSeconds: 5,
        aspectRatio: '16:9',
      },
    });

    if (!operation) {
      throw new Error('Expected the model to return an operation');
    }

    console.log('Video generation operation started. Polling for completion...');

    // Poll for completion
    while (!operation.done) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      operation = await ai.checkOperation(operation);
      console.log('Polling... Operation status:', operation.done);
    }

    if (operation.error) {
      console.error('Video generation failed:', operation.error);
      throw new Error('Failed to generate video: ' + operation.error.message);
    }

    const videoPart = operation.output?.message?.content.find(p => !!p.media);
    if (!videoPart || !videoPart.media?.url) {
      console.error('No video found in operation output');
      throw new Error('Failed to find the generated video in the operation result.');
    }
    
    console.log('Video generation completed.');

    // IMPORTANT: The URL from the operation is temporary and requires an API key for access.
    // For client-side display, we must fetch it server-side and convert to a Data URI.
    const fetch = (await import('node-fetch')).default;
    const videoDownloadResponse = await fetch(
      `${videoPart.media.url}&key=${process.env.GEMINI_API_KEY}`
    );

    if (!videoDownloadResponse.ok || !videoDownloadResponse.body) {
      throw new Error(`Failed to download video. Status: ${videoDownloadResponse.status}`);
    }

    const videoBuffer = await videoDownloadResponse.arrayBuffer();
    const base64Video = Buffer.from(videoBuffer).toString('base64');
    const contentType = videoPart.media.contentType || 'video/mp4';
    const videoUrl = `data:${contentType};base64,${base64Video}`;

    return { videoUrl };
  }
);


// Exported server action that wraps the flow
export async function generateVideo(
  input: GenerateVideoInput
): Promise<GenerateVideoOutput> {
  // Mock implementation - returns a placeholder video URL without API key
  return generateMockVideo(input);
}

// Mock video generation function
function generateMockVideo(input: GenerateVideoInput): GenerateVideoOutput {
  // Return a placeholder video URL - in a real implementation, this could be
  // a pre-generated video or a simple animation
  const mockVideoUrl = `data:video/mp4;base64,placeholder_video_data_for_${encodeURIComponent(input.prompt)}`;
  
  return {
    videoUrl: mockVideoUrl
  };
}
