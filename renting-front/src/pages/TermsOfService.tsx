import React from 'react';
import AppLayout from '@/components/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const TermsOfService: React.FC = () => {
  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold">Terms of Service</CardTitle>
            <p className="text-muted-foreground">Last updated: July 18, 2025</p>
          </CardHeader>
          <CardContent className="prose max-w-none">
            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">1. Acceptance of Terms</h2>
              <p className="mb-4">
                By accessing and using ComfyRent, you accept and agree to be bound by the terms and provision of this agreement. 
                If you do not agree to abide by the above, please do not use this service.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">2. Service Description</h2>
              <p className="mb-4">
                ComfyRent is a real estate platform that connects property owners with potential tenants. We guarantee a single 
                listing per property for your searching comfort and provide tools for property management and rental applications.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">3. User Responsibilities</h2>
              <p className="mb-4">As a user of our platform, you agree to:</p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Provide accurate and truthful information</li>
                <li>Maintain the security of your account credentials</li>
                <li>Use the platform only for legitimate rental purposes</li>
                <li>Respect the rights and privacy of other users</li>
                <li>Comply with all applicable laws and regulations</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">4. Property Listings</h2>
              <p className="mb-4">Property owners and managers agree to:</p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Provide accurate property descriptions and photos</li>
                <li>Honor the single listing per property guarantee</li>
                <li>Respond promptly to legitimate inquiries</li>
                <li>Comply with fair housing laws and regulations</li>
                <li>Keep listing information up to date</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">5. Prohibited Activities</h2>
              <p className="mb-4">Users are prohibited from:</p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Creating duplicate listings for the same property</li>
                <li>Posting false or misleading information</li>
                <li>Harassing or discriminating against other users</li>
                <li>Using the platform for illegal activities</li>
                <li>Attempting to circumvent platform security measures</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">6. Platform Availability</h2>
              <p className="mb-4">
                While we strive to maintain continuous service, ComfyRent may be temporarily unavailable due to maintenance, 
                updates, or technical issues. We do not guarantee uninterrupted access to the platform.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">7. Limitation of Liability</h2>
              <p className="mb-4">
                ComfyRent serves as a platform connecting users and is not responsible for the conduct of users or the 
                accuracy of listings. Users engage with each other at their own risk.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">8. Changes to Terms</h2>
              <p className="mb-4">
                We reserve the right to modify these terms at any time. Users will be notified of significant changes, 
                and continued use of the platform constitutes acceptance of the modified terms.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">9. Contact Information</h2>
              <p className="mb-4">
                For questions about these Terms of Service, please contact us at:
              </p>
              <div className="bg-muted p-4 rounded-lg">
                <p><strong>Email:</strong> info.nextep.solutions@gmail.com</p>
                <p><strong>Phone:</strong> + 995599738023</p>
              </div>
            </section>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
};

export default TermsOfService;
