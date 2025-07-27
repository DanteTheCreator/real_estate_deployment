import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AppLayout } from '@/components/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Edit, Trash2, Eye, Heart, Settings, Plus, Loader2 } from 'lucide-react';
import { dashboardService, MyListing, DashboardStats } from '@/services/dashboardService';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { Property } from '@/types';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { formatPrice } = useCurrency();
  const navigate = useNavigate();
  const [myListings, setMyListings] = useState<MyListing[]>([]);
  const [savedListings, setSavedListings] = useState<Property[]>([]);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || ''
  });
  const { toast } = useToast();

  // Update profile data when user changes
  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || ''
      });
    }
  }, [user]);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Always load stats (mock data)
        const stats = await dashboardService.getDashboardStats();
        setDashboardStats(stats);
        
        // Try to load listings and saved properties, but handle errors gracefully
        try {
          const listings = await dashboardService.getMyListings();
          setMyListings(listings);
        } catch (error) {
          console.warn('Could not load my listings:', error);
          setMyListings([]);
        }
        
        try {
          const saved = await dashboardService.getSavedListings();
          setSavedListings(saved);
        } catch (error) {
          console.warn('Could not load saved listings:', error);
          setSavedListings([]);
        }
        
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        toast({
          title: t('common.error'),
          description: t('toast.dashboardError'),
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [toast, t]);

  const handleDeleteListing = async (id: number) => {
    try {
      await dashboardService.deleteListing(id.toString());
      setMyListings(prev => prev.filter(listing => listing.id !== id));
      toast({
        title: t('common.success'),
        description: t('toast.listingDeleted'),
      });
    } catch (error) {
      console.error('Error deleting listing:', error);
      toast({
        title: t('common.error'),
        description: t('toast.deleteError'),
        variant: "destructive",
      });
    }
  };

  const handleEditListing = (id: number) => {
    navigate(`/edit-property/${id}`);
  };

  const handleToggleFavorite = async (propertyId: number) => {
    try {
      await dashboardService.toggleFavorite(propertyId.toString());
      setSavedListings(prev => prev.filter(listing => listing.id !== propertyId));
      toast({
        title: t('common.success'),
        description: t('toast.removedFavorites'),
      });
    } catch (error) {
      console.error('Error toggling favorite:', error);
      toast({
        title: t('common.error'),
        description: t('toast.favoritesError'),
        variant: "destructive",
      });
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await dashboardService.updateProfile(profileData);
      toast({
        title: t('common.success'),
        description: t('toast.profileUpdated'),
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      toast({
        title: t('common.error'),
        description: t('toast.profileError'),
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="py-8 flex items-center justify-center min-h-[400px]">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      </AppLayout>
    );
  }
  
  return (
    <AppLayout>
      <div className="py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">{t('dashboard.title')}</h1>
            {user && (
              <p className="text-sm text-muted-foreground mt-1">
                {t('dashboard.welcome')}, {user.first_name} {user.last_name}
              </p>
            )}
          </div>
        </div>
          
          <Tabs defaultValue="listings" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="listings">{t('dashboard.myListings')}</TabsTrigger>
              <TabsTrigger value="saved">{t('dashboard.saved')}</TabsTrigger>
              <TabsTrigger value="analytics">{t('dashboard.analytics')}</TabsTrigger>
              <TabsTrigger value="settings">{t('dashboard.settings')}</TabsTrigger>
            </TabsList>
            
            <TabsContent value="listings" className="space-y-4">
              <div className="grid gap-4">
                {myListings.length > 0 ? (
                  myListings.map((listing) => (
                    <Card key={listing.id} className="group hover:shadow-lg transition-shadow duration-300">
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                          <Link 
                            to={`/property/${listing.id}`}
                            className="flex-1 cursor-pointer"
                          >
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors">{listing.title}</h3>
                              <div className="flex items-center gap-4 text-sm text-slate-600">
                                <span className="font-medium">{formatPrice(listing.rent_amount, listing.rent_amount_usd, listing.listing_type)}</span>
                                <Badge variant={listing.status === 'active' ? 'default' : 'secondary'}>
                                  {listing.status === 'active' ? t('common.active') : t('common.inactive')}
                                </Badge>
                                <span className="flex items-center gap-1">
                                  <Eye className="w-4 h-4" />
                                  {listing.views} {t('dashboard.views')}
                                </span>
                              </div>
                            </div>
                          </Link>
                          <div className="flex gap-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => handleEditListing(listing.id)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => handleDeleteListing(listing.id)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-muted-foreground mb-4">{t('dashboard.noListings')}</p>
                      <p className="text-sm text-muted-foreground">
                        {t('dashboard.createFirst')}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="saved" className="space-y-4">
              <div className="grid gap-4">
                {savedListings.length > 0 ? (
                  savedListings.map((listing) => (
                    <Card key={listing.id} className="group hover:shadow-lg transition-shadow duration-300">
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                          <Link 
                            to={`/property/${listing.id}`}
                            className="flex-1 cursor-pointer"
                          >
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors">{listing.title}</h3>
                              <div className="flex items-center gap-4 text-sm text-slate-600">
                                <span className="font-medium">{formatPrice(listing.rent_amount, listing.rent_amount_usd, listing.listing_type)}</span>
                                <span>{listing.city}, {listing.state}</span>
                              </div>
                            </div>
                          </Link>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleFavorite(listing.id);
                            }}
                          >
                            <Heart className="w-4 h-4 fill-current" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-muted-foreground">{t('dashboard.noSaved')}</p>
                      <p className="text-sm text-muted-foreground mt-2">
                        {t('dashboard.browseSaved')}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="analytics">
              <Card>
                <CardHeader>
                  <CardTitle className="text-slate-800">{t('dashboard.analyticsTitle')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600 mb-2">
                        {dashboardStats?.totalViews || 0}
                      </div>
                      <div className="text-slate-600">{t('dashboard.totalViews')}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600 mb-2">
                        {dashboardStats?.inquiries || 0}
                      </div>
                      <div className="text-slate-600">{t('dashboard.inquiries')}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600 mb-2">
                        {dashboardStats?.activeListings || 0}
                      </div>
                      <div className="text-slate-600">{t('dashboard.activeListings')}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-orange-600 mb-2">
                        {dashboardStats?.savedListings || 0}
                      </div>
                      <div className="text-slate-600">{t('dashboard.savedProperties')}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="settings">
              <Card>
                <CardHeader>
                  <CardTitle className="text-slate-800 flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    {t('dashboard.accountSettings')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleUpdateProfile} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="firstName" className="text-sm font-medium text-slate-700">{t('dashboard.firstName')}</Label>
                        <Input 
                          id="firstName"
                          value={profileData.first_name}
                          onChange={(e) => setProfileData(prev => ({ ...prev, first_name: e.target.value }))}
                          placeholder={t('dashboard.enterFirstName')}
                        />
                      </div>
                      <div>
                        <Label htmlFor="lastName" className="text-sm font-medium text-slate-700">{t('dashboard.lastName')}</Label>
                        <Input 
                          id="lastName"
                          value={profileData.last_name}
                          onChange={(e) => setProfileData(prev => ({ ...prev, last_name: e.target.value }))}
                          placeholder={t('dashboard.enterLastName')}
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="email" className="text-sm font-medium text-slate-700">{t('dashboard.email')}</Label>
                      <Input 
                        id="email"
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                        placeholder={t('dashboard.enterEmail')}
                      />
                    </div>
                    <div>
                      <Label htmlFor="phone" className="text-sm font-medium text-slate-700">{t('dashboard.phone')}</Label>
                      <Input 
                        id="phone"
                        value={profileData.phone}
                        onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
                        placeholder={t('dashboard.enterPhone')}
                      />
                    </div>
                    <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                      {t('dashboard.saveChanges')}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </AppLayout>
  );
};

export default Dashboard;