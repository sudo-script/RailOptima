import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

const logData = [
  { 
    id: 1, 
    timestamp: '10:32:15', 
    user: 'Ctrl_Sharma', 
    action: 'Accepted' as const, 
    details: 'Divert 12301 via Agra loop',
    outcome: 'Successful. 12301 crossed Ghaziabad with a 25 min delay.',
    reason: '',
  },
  { 
    id: 2, 
    timestamp: '10:28:45', 
    user: 'Ctrl_Patel', 
    action: 'Overridden' as const, 
    details: 'Hold 22439 at Ambala Cantt',
    outcome: 'Minor delay. 22439 delayed by 15 mins.',
    reason: 'Platform congestion at New Delhi.',
  },
  { 
    id: 3, 
    timestamp: '10:25:02', 
    user: 'SYSTEM', 
    action: 'Generated' as const, 
    details: 'Signal Failure at Ghaziabad',
    outcome: 'Pending operator action.',
    reason: '',
  },
];

const actionConfig = {
    'Accepted': { variant: 'default' as const, icon: <CheckCircle2 className="text-green-500" /> },
    'Overridden': { variant: 'destructive' as const, icon: <XCircle className="text-red-500" /> },
    'Generated': { variant: 'secondary' as const, icon: <AlertCircle className="text-yellow-500" /> },
};


export default function DecisionLog() {
  return (
    <div className='max-h-[60vh] overflow-y-auto'>
        <h3 className="font-semibold text-foreground mb-4">Chronological Decision History</h3>
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[100px]">Timestamp</TableHead>
                    <TableHead className="w-[100px]">User</TableHead>
                    <TableHead className="w-[120px]">Action</TableHead>
                    <TableHead>Details</TableHead>
                    <TableHead>Outcome / Reason</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {logData.map((log) => (
                    <TableRow key={log.id} className='text-xs'>
                        <TableCell className="font-mono">{log.timestamp}</TableCell>
                        <TableCell>{log.user}</TableCell>
                        <TableCell>
                            <div className='flex items-center gap-2'>
                              {actionConfig[log.action].icon}
                              <Badge variant={actionConfig[log.action].variant}>{log.action}</Badge>
                            </div>
                        </TableCell>
                        <TableCell>{log.details}</TableCell>
                        <TableCell>
                          <p>{log.outcome}</p>
                          {log.reason && <p className='text-muted-foreground italic'>"{log.reason}"</p>}
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    </div>
  );
}
