import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { contactService, ReportData } from '@/services/contactService';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

interface ReportPropertyDialogProps {
  isOpen: boolean;
  onClose: () => void;
  propertyId: string;
  propertyTitle: string;
}

const REPORT_REASONS = [
  { value: 'inappropriate_content', label: 'Inappropriate Content' },
  { value: 'misleading_info', label: 'Misleading Information' },
  { value: 'spam', label: 'Spam/Duplicate Listing' },
  { value: 'wrong_price', label: 'Incorrect Price' },
  { value: 'wrong_location', label: 'Wrong Location' },
  { value: 'not_available', label: 'Property Not Available' },
  { value: 'fraud', label: 'Suspected Fraud' },
  { value: 'other', label: 'Other' },
];

export const ReportPropertyDialog: React.FC<ReportPropertyDialogProps> = ({
  isOpen,
  onClose,
  propertyId,
  propertyTitle,
}) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reportData, setReportData] = useState({
    reportReason: '',
    description: '',
    userEmail: user?.email || '',
    userName: user ? `${user.first_name} ${user.last_name}` : '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!reportData.reportReason) {
      toast({
        title: 'Error',
        description: 'Please select a reason for reporting.',
        variant: 'destructive',
      });
      return;
    }

    if (!reportData.description.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a description of the issue.',
        variant: 'destructive',
      });
      return;
    }

    setIsSubmitting(true);
    
    try {
      const selectedReason = REPORT_REASONS.find(r => r.value === reportData.reportReason);
      
      await contactService.sendPropertyReport({
        propertyId,
        propertyTitle,
        reportReason: selectedReason?.label || reportData.reportReason,
        description: reportData.description,
        userEmail: reportData.userEmail || undefined,
        userName: reportData.userName || undefined,
      });

      toast({
        title: 'Report Sent',
        description: 'Thank you for your report. We will investigate this property listing.',
      });

      onClose();
      
      // Reset form
      setReportData({
        reportReason: '',
        description: '',
        userEmail: user?.email || '',
        userName: user ? `${user.first_name} ${user.last_name}` : '',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to send report. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            Report Property
          </DialogTitle>
          <DialogDescription>
            Help us maintain quality listings by reporting issues with this property.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="reason">Reason for reporting</Label>
            <Select
              value={reportData.reportReason}
              onValueChange={(value) => setReportData(prev => ({ ...prev, reportReason: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a reason" />
              </SelectTrigger>
              <SelectContent>
                {REPORT_REASONS.map((reason) => (
                  <SelectItem key={reason.value} value={reason.value}>
                    {reason.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Please provide details about the issue..."
              value={reportData.description}
              onChange={(e) => setReportData(prev => ({ ...prev, description: e.target.value }))}
              className="min-h-[100px]"
              required
            />
          </div>

          {!user && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="userName">Your Name (Optional)</Label>
                <Input
                  id="userName"
                  placeholder="Enter your name"
                  value={reportData.userName}
                  onChange={(e) => setReportData(prev => ({ ...prev, userName: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="userEmail">Your Email (Optional)</Label>
                <Input
                  id="userEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={reportData.userEmail}
                  onChange={(e) => setReportData(prev => ({ ...prev, userEmail: e.target.value }))}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                'Send Report'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
