import { apiService } from './apiService';

export interface ContactData {
  name: string;
  email: string;
  subject: string;
  message: string;
  propertyId?: string;
}

export interface ReportData {
  propertyId: string;
  propertyTitle: string;
  reportReason: string;
  description: string;
  userEmail?: string;
  userName?: string;
}

export const contactService = {
  // Send general contact email
  async sendContactEmail(contactData: ContactData): Promise<void> {
    // Since there's no backend endpoint for email, we'll use mailto for now
    // but this structure allows for easy backend integration later
    const subject = encodeURIComponent(contactData.subject);
    const body = encodeURIComponent(
      `Name: ${contactData.name}\n` +
      `Email: ${contactData.email}\n\n` +
      `Message:\n${contactData.message}` +
      (contactData.propertyId ? `\n\nProperty ID: ${contactData.propertyId}` : '')
    );
    
    window.location.href = `mailto:info.nextep.solutions@gmail.com?subject=${subject}&body=${body}`;
  },

  // Send property report email
  async sendPropertyReport(reportData: ReportData): Promise<void> {
    const subject = encodeURIComponent(`Report - ${reportData.propertyTitle}`);
    const body = encodeURIComponent(
      `Property Report\n` +
      `================\n\n` +
      `Property ID: ${reportData.propertyId}\n` +
      `Property Title: ${reportData.propertyTitle}\n` +
      `Report Reason: ${reportData.reportReason}\n\n` +
      `Description:\n${reportData.description}\n\n` +
      `Reported by:\n` +
      `Name: ${reportData.userName || 'Anonymous'}\n` +
      `Email: ${reportData.userEmail || 'Not provided'}\n\n` +
      `Please investigate this property listing.`
    );
    
    window.location.href = `mailto:info.nextep.solutions@gmail.com?subject=${subject}&body=${body}`;
  },

  // Generate shareable property link
  generateShareLink(propertyId: string, propertyTitle: string): string {
    const baseUrl = window.location.origin;
    return `${baseUrl}/property/${propertyId}`;
  },

  // Share property via Web Share API or fallback to clipboard
  async shareProperty(propertyId: string, propertyTitle: string, propertyPrice?: number): Promise<boolean> {
    const shareUrl = this.generateShareLink(propertyId, propertyTitle);
    const shareText = `Check out this property: ${propertyTitle}${propertyPrice ? ` - ₾${propertyPrice.toLocaleString()}` : ''}`;

    // Try Web Share API first (mobile devices)
    if (navigator.share) {
      try {
        await navigator.share({
          title: `ComfyRent - ${propertyTitle}`,
          text: shareText,
          url: shareUrl,
        });
        return true;
      } catch (error) {
        // User cancelled or error occurred, fall back to clipboard
      }
    }

    // Fallback to clipboard
    try {
      await navigator.clipboard.writeText(shareUrl);
      return true;
    } catch (error) {
      // If clipboard fails, try the old way
      try {
        const textArea = document.createElement('textarea');
        textArea.value = shareUrl;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        return successful;
      } catch (fallbackError) {
        console.error('Failed to copy to clipboard:', fallbackError);
        return false;
      }
    }
  },

  // Generate social media share URLs
  generateSocialShareUrls(propertyId: string, propertyTitle: string, propertyPrice?: number) {
    const shareUrl = this.generateShareLink(propertyId, propertyTitle);
    const shareText = `Check out this property: ${propertyTitle}${propertyPrice ? ` - ₾${propertyPrice.toLocaleString()}` : ''}`;
    
    return {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
      twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
      whatsapp: `https://wa.me/?text=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`,
      telegram: `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`,
      email: `mailto:?subject=${encodeURIComponent(`Property: ${propertyTitle}`)}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`,
    };
  },
};
