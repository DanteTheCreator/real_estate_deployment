import React from 'react';
import AppLayout from '@/components/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const PrivacyPolicy: React.FC = () => {
  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold">Privacy Policy</CardTitle>
            <p className="text-muted-foreground">Last updated: July 18, 2025</p>
          </CardHeader>
          <CardContent className="prose max-w-none">
            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">1. Information We Collect</h2>
              <p className="mb-4">
                At ComfyRent, we collect information you provide directly to us, such as when you create an account, 
                list a property, search for properties, or contact us for support.
              </p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Personal information (name, email address, phone number)</li>
                <li>Property information and photos</li>
                <li>Communication preferences</li>
                <li>Usage data and analytics</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">2. How We Use Your Information</h2>
              <p className="mb-4">We use the information we collect to:</p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Provide and maintain our real estate platform services</li>
                <li>Process property listings and rental applications</li>
                <li>Communicate with you about our services</li>
                <li>Improve our platform and user experience</li>
                <li>Ensure platform security and prevent fraud</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">3. Information Sharing</h2>
              <p className="mb-4">
                We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, 
                except as described in this policy. We may share information with:
              </p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Service providers who assist us in operating our platform</li>
                <li>Legal authorities when required by law</li>
                <li>Property owners and tenants for legitimate rental purposes</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">4. Data Security</h2>
              <p className="mb-4">
                We implement appropriate security measures to protect your personal information against unauthorized access, 
                alteration, disclosure, or destruction. However, no method of transmission over the internet is 100% secure.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">5. Your Rights</h2>
              <p className="mb-4">You have the right to:</p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Access and update your personal information</li>
                <li>Delete your account and associated data</li>
                <li>Opt-out of marketing communications</li>
                <li>Request data portability</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">6. Contact Us</h2>
              <p className="mb-4">
                If you have any questions about this Privacy Policy, please contact us at:
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

export default PrivacyPolicy;
