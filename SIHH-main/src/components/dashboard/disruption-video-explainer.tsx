
'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Info, Loader2, PlayCircle, AlertTriangle } from 'lucide-react';
import { generateVideo, GenerateVideoInput } from '@/ai/flows/generate-video-flow';
import { Alert, AlertTitle, AlertDescription as UIDescription } from '@/components/ui/alert';

type DisruptionVideoExplainerProps = {
  disruptionType: string;
};

export default function DisruptionVideoExplainer({
  disruptionType,
}: DisruptionVideoExplainerProps) {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const handleGenerateVideo = async () => {
    setIsLoading(true);
    setError(null);
    setVideoUrl(null);
    try {
      const input: GenerateVideoInput = {
        prompt: `A brief explanation of a "${disruptionType}" on the railway.`,
      };
      const result = await generateVideo(input);
      setVideoUrl(result.videoUrl);
    } catch (e: any) {
      console.error('Video generation failed:', e);
      let errorMessage = 'An unknown error occurred while generating the video.';
      if (e.message && e.message.includes('billing enabled')) {
        errorMessage = 'Video generation requires a Google Cloud Platform project with billing enabled. Please check your project configuration.';
      } else if (e.message) {
        errorMessage = e.message;
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) {
      // Reset state when dialog is closed
      setVideoUrl(null);
      setIsLoading(false);
      setError(null);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-5 w-5 text-muted-foreground hover:bg-transparent hover:text-primary"
          aria-label={`Learn more about ${disruptionType}`}
        >
          <Info className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[625px]">
        <DialogHeader>
          <DialogTitle>What is a "{disruptionType}"?</DialogTitle>
          <DialogDescription>
            Generate a short AI video to learn more about this type of disruption.
          </DialogDescription>
        </DialogHeader>
        <div className="mt-4 aspect-video w-full flex items-center justify-center bg-muted rounded-lg border">
          {isLoading ? (
            <div className="flex flex-col items-center gap-2 text-muted-foreground">
              <Loader2 className="h-8 w-8 animate-spin" />
              <p>Generating video... this may take a moment.</p>
            </div>
          ) : error ? (
            <Alert variant="destructive" className="m-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Generation Failed</AlertTitle>
              <UIDescription>
                Could not generate the video. Please try again later.
                <p className="text-xs mt-2 font-mono">{error}</p>
              </UIDescription>
            </Alert>
          ) : videoUrl ? (
            <video src={videoUrl} controls autoPlay className="w-full h-full rounded-lg" />
          ) : (
            <div className="text-center text-muted-foreground">
                <p className='mb-4'>Click the button below to generate an explanation video.</p>
                 <Button onClick={handleGenerateVideo} disabled={isLoading}>
                    <PlayCircle className="mr-2" />
                    Generate Video
                </Button>
            </div>
          )}
        </div>
        <div className="mt-4 flex justify-end">
           <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
