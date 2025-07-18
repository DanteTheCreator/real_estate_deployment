import React from 'react';
import AppLayout from '@/components/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const CookiePolicy: React.FC = () => {
  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold">Cookie Policy</CardTitle>
            <p className="text-muted-foreground">Last updated: July 18, 2025</p>
          </CardHeader>
          <CardContent className="prose max-w-none">
            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">1. What Are Cookies</h2>
              <p className="mb-4">
                Cookies are small text files that are stored on your device when you visit our website. They help us provide 
                you with a better experience by remembering your preferences and improving our services.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">2. How We Use Cookies</h2>
              <p className="mb-4">ComfyRent uses cookies for several purposes:</p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li><strong>Essential Cookies:</strong> Required for basic website functionality</li>
                <li><strong>Authentication Cookies:</strong> To keep you logged in securely</li>
                <li><strong>Preference Cookies:</strong> To remember your settings and preferences</li>
                <li><strong>Analytics Cookies:</strong> To understand how users interact with our platform</li>
                <li><strong>Security Cookies:</strong> To protect against fraud and enhance security</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">3. Types of Cookies We Use</h2>
              
              <div className="mb-4">
                <h3 className="text-xl font-semibold mb-2">Session Cookies</h3>
                <p className="mb-2">
                  These are temporary cookies that expire when you close your browser. They help maintain your session 
                  while browsing our platform.
                </p>
              </div>

              <div className="mb-4">
                <h3 className="text-xl font-semibold mb-2">Persistent Cookies</h3>
                <p className="mb-2">
                  These cookies remain on your device for a set period or until you delete them. They help us remember 
                  your preferences across visits.
                </p>
              </div>

              <div className="mb-4">
                <h3 className="text-xl font-semibold mb-2">Third-Party Cookies</h3>
                <p className="mb-2">
                  We may use services from third parties that place cookies on your device to provide analytics and 
                  improve our services.
                </p>
              </div>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">4. Cookie Management</h2>
              <p className="mb-4">You have several options for managing cookies:</p>
              <ul className="list-disc list-inside mb-4 space-y-2">
                <li>Most browsers allow you to view, manage, and delete cookies</li>
                <li>You can set your browser to refuse all cookies or notify you when cookies are being sent</li>
                <li>Disabling cookies may affect the functionality of our platform</li>
                <li>You can opt-out of analytics cookies through browser settings</li>
              </ul>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">5. Browser Settings</h2>
              <p className="mb-4">To manage cookies in popular browsers:</p>
              
              <div className="bg-muted p-4 rounded-lg mb-4">
                <p><strong>Chrome:</strong> Settings → Privacy and Security → Cookies and other site data</p>
                <p><strong>Firefox:</strong> Settings → Privacy & Security → Cookies and Site Data</p>
                <p><strong>Safari:</strong> Preferences → Privacy → Manage Website Data</p>
                <p><strong>Edge:</strong> Settings → Cookies and site permissions → Cookies and site data</p>
              </div>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">6. Updates to This Policy</h2>
              <p className="mb-4">
                We may update this Cookie Policy from time to time to reflect changes in our practices or for legal 
                reasons. We will notify you of any significant changes by posting the new policy on our website.
              </p>
            </section>

            <section className="mb-6">
              <h2 className="text-2xl font-semibold mb-3">7. Contact Us</h2>
              <p className="mb-4">
                If you have any questions about our use of cookies, please contact us at:
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

export default CookiePolicy;
