import { AlertTriangle, CircleStop, Clock, UserX, Siren } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '../ui/button';
import { cn } from '@/lib/utils';
import DisruptionVideoExplainer from './disruption-video-explainer';


type Disruption = {
  type: 'Signal Failure' | 'Track Blockage' | 'Passenger Incident' | 'Delay';
  severity: 'Low' | 'Medium' | 'High';
  location: string;
  details: string;
  affectedTrains: string[];
  isEmergency?: boolean;
};

type DisruptionsPanelProps = {
  disruptions: Disruption[];
  onShowAlert: () => void;
};

const iconMap = {
  'Signal Failure': <AlertTriangle className="h-5 w-5 text-yellow-500" />,
  'Track Blockage': <CircleStop className="h-5 w-5 text-destructive" />,
  'Passenger Incident': <UserX className="h-5 w-5 text-blue-500" />,
  'Delay': <Clock className="h-5 w-5 text-orange-500" />,
};

const severityMap = {
    'Low': 'bg-green-500/20 text-green-700 border-green-500/30',
    'Medium': 'bg-yellow-500/20 text-yellow-700 border-yellow-500/30',
    'High': 'bg-red-500/20 text-red-700 border-red-500/30',
};


export default function DisruptionsPanel({ disruptions, onShowAlert }: DisruptionsPanelProps) {
  return (
    <div className='flex flex-col h-full'>
      <h2 className="text-lg font-semibold mb-4 text-foreground">Disruptions Queue</h2>
      <div className="space-y-3 overflow-y-auto max-h-[calc(80vh-100px)] pr-2">
        {disruptions.map((disruption, index) => (
          <div 
            key={index} 
            className={cn(
              "flex items-start gap-4 p-3 bg-muted/50 rounded-lg border hover:border-primary/50 transition-all",
              disruption.isEmergency && "border-destructive/50 ring-2 ring-destructive/20 shadow-lg shadow-destructive/10"
            )}
          >
            <div className="pt-1">
              {iconMap[disruption.type]}
            </div>
            <div className='w-full'>
              <div className="flex justify-between items-center mb-1">
                 <div className='flex items-center gap-2'>
                   <h3 className="font-semibold text-foreground">{disruption.type}</h3>
                   <DisruptionVideoExplainer disruptionType={disruption.type}/>
                 </div>
                 <Badge className={`text-xs ${severityMap[disruption.severity]}`}>{disruption.severity}</Badge>
              </div>
              <p className="text-sm text-muted-foreground font-medium mb-2">{disruption.location}</p>
              <p className="text-sm text-muted-foreground mb-3">{disruption.details}</p>
              
              <div className="mb-3">
                 <span className="text-xs font-medium text-muted-foreground">Affected Trains:</span>
                 <div className="flex flex-wrap gap-1 mt-1">
                  {disruption.affectedTrains.map(trainId => (
                    <Badge key={trainId} variant="outline" className="text-xs">{trainId}</Badge>
                  ))}
                 </div>
              </div>
              <div className='flex items-center justify-end'>
                <div className='flex items-center gap-2'>
                    {disruption.isEmergency ? (
                      <Button variant="destructive" size="sm" className='text-xs h-7 gap-1.5' onClick={onShowAlert}>
                        <Siren className='w-3.5 h-3.5'/>
                        View Alert
                      </Button>
                    ) : (
                      <>
                        <Button variant="outline" size="sm" className='text-xs h-7'>Update Status</Button>
                        <Button variant="ghost" size="sm" className='text-xs h-7'>View Details</Button>
                      </>
                    )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
