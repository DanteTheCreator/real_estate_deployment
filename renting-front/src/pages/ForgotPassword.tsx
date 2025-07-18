import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AppLayout } from '@/components/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Mail, ArrowLeft, Building } from 'lucide-react';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle forgot password logic here
    console.log('Password reset requested for:', email);
    setIsSubmitted(true);
  };

  return (
    <AppLayout>
      <div className="min-h-[80vh] flex items-center justify-center py-12">
          <div className="w-full max-w-md">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-2 mb-4">
                <Building className="w-8 h-8 text-primary" />
                <h1 className="text-3xl font-bold text-foreground">ComfyRent</h1>
              </div>
              <p className="text-muted-foreground">Reset your password</p>
            </div>

            <Card className="shadow-lg">
              <CardHeader className="space-y-1">
                <CardTitle className="text-center text-foreground">
                  {isSubmitted ? 'Check Your Email' : 'Forgot Password'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!isSubmitted ? (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-foreground">Email Address</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="email"
                          type="email"
                          placeholder="Enter your email address"
                          className="pl-10"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          required
                        />
                      </div>
                    </div>

                    <div className="text-sm text-muted-foreground">
                      Enter the email address associated with your account and we'll send you a link to reset your password.
                    </div>

                    <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
                      Send Reset Link
                    </Button>

                    <div className="text-center">
                      <Link to="/auth" className="text-sm text-primary hover:text-primary/80 flex items-center justify-center gap-1">
                        <ArrowLeft className="w-3 h-3" />
                        Back to Login
                      </Link>
                    </div>
                  </form>
                ) : (
                  <div className="text-center space-y-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                      <Mail className="w-6 h-6 text-primary" />
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold text-foreground">Email Sent!</h3>
                      <p className="text-sm text-muted-foreground">
                        We've sent a password reset link to <span className="font-medium">{email}</span>
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Please check your email and follow the instructions to reset your password.
                      </p>
                    </div>
                    
                    <div className="space-y-3">
                      <Button 
                        onClick={() => setIsSubmitted(false)} 
                        variant="outline" 
                        className="w-full"
                      >
                        Resend Email
                      </Button>
                      
                      <Link to="/auth" className="block">
                        <Button variant="ghost" className="w-full">
                          <ArrowLeft className="w-4 h-4 mr-2" />
                          Back to Login
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="text-center mt-6">
              <p className="text-sm text-muted-foreground">
                Need help? Contact our{' '}
                <a href="#" className="text-primary hover:text-primary/80">customer support</a>
              </p>
            </div>
          </div>
        </div>
      </AppLayout>
  );
};

export default ForgotPassword;
