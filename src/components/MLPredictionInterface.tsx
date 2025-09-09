import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Calendar, Thermometer, Droplets, Truck, Package, TrendingUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface PredictionData {
  temperature: number;
  humidity: number;
  transportation_time: number;
  date: string;
}

interface PredictionResult {
  predicted_packaging: string;
  probability_plastic: number;
  confidence: number;
}

const MLPredictionInterface = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState<PredictionData>({
    temperature: 25.0,
    humidity: 60.0,
    transportation_time: 5.0,
    date: new Date().toISOString().split('T')[0]
  });
  
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: keyof PredictionData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: field === 'date' ? value : Number(value)
    }));
  };

  const handlePredict = async () => {
    try {
      setIsLoading(true);
      
      // Mock API call - replace with your Flask endpoint
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Prediction failed');
      
      const result = await response.json();
      setPrediction(result);
      
      toast({
        title: "Prediction Complete",
        description: `Recommended packaging: ${result.predicted_packaging}`,
      });
    } catch (error) {
      // Mock prediction for demo
      const mockResult: PredictionResult = {
        predicted_packaging: "Plastic",
        probability_plastic: 0.8547,
        confidence: 85.47
      };
      setPrediction(mockResult);
      
      toast({
        title: "Demo Prediction",
        description: "Using mock data - connect your Flask API",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <Card className="bg-gradient-surface border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Package className="w-5 h-5 text-primary" />
            Supply Chain Packaging Predictor
          </CardTitle>
          <CardDescription>
            Enter environmental and logistics data to predict optimal packaging type
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="temperature" className="flex items-center gap-2">
                <Thermometer className="w-4 h-4 text-destructive" />
                Temperature (°C)
              </Label>
              <Input
                id="temperature"
                type="number"
                step="0.1"
                value={formData.temperature}
                onChange={(e) => handleInputChange('temperature', e.target.value)}
                className="bg-ml-surface border-border hover:border-primary/50 transition-smooth"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="humidity" className="flex items-center gap-2">
                <Droplets className="w-4 h-4 text-secondary" />
                Humidity (%)
              </Label>
              <Input
                id="humidity"
                type="number"
                step="0.1"
                value={formData.humidity}
                onChange={(e) => handleInputChange('humidity', e.target.value)}
                className="bg-ml-surface border-border hover:border-primary/50 transition-smooth"
              />
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="transportation_time" className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-accent" />
                Transportation Time (days)
              </Label>
              <Input
                id="transportation_time"
                type="number"
                step="0.1"
                value={formData.transportation_time}
                onChange={(e) => handleInputChange('transportation_time', e.target.value)}
                className="bg-ml-surface border-border hover:border-primary/50 transition-smooth"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="date" className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-primary" />
                Date
              </Label>
              <Input
                id="date"
                type="date"
                value={formData.date}
                onChange={(e) => handleInputChange('date', e.target.value)}
                className="bg-ml-surface border-border hover:border-primary/50 transition-smooth"
              />
            </div>
          </div>
        </CardContent>
        
        <div className="px-6 pb-6">
          <Button 
            variant="predict" 
            size="lg" 
            onClick={handlePredict}
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Analyzing...
              </>
            ) : (
              <>
                <TrendingUp className="w-4 h-4" />
                Predict Packaging
              </>
            )}
          </Button>
        </div>
      </Card>

      {/* Prediction Results */}
      {prediction && (
        <Card className="bg-ml-surface border-primary/20 shadow-data">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="w-5 h-5 text-prediction-success" />
              Prediction Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Recommended Packaging</p>
                <Badge variant="outline" className="bg-gradient-data text-white border-none text-lg px-4 py-2">
                  {prediction.predicted_packaging}
                </Badge>
              </div>
              
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Plastic Probability</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-border rounded-full h-3 overflow-hidden">
                    <div 
                      className="h-full bg-gradient-primary transition-all duration-1000 ease-out"
                      style={{ width: `${prediction.probability_plastic * 100}%` }}
                    />
                  </div>
                  <span className="text-lg font-semibold text-primary">
                    {(prediction.probability_plastic * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
            
            <div className="mt-4 p-4 bg-ml-surface-hover rounded-lg border border-border">
              <p className="text-sm text-muted-foreground mb-2">Model Confidence</p>
              <div className="flex items-center gap-2">
                <div className="text-2xl font-bold text-prediction-success">
                  {prediction.confidence.toFixed(1)}%
                </div>
                <Badge variant={prediction.confidence > 80 ? "default" : "secondary"}>
                  {prediction.confidence > 80 ? "High Confidence" : "Medium Confidence"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MLPredictionInterface;