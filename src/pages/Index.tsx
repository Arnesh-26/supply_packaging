import React from 'react';
import MLPredictionInterface from "@/components/MLPredictionInterface";
import ChatBot from "@/components/ChatBot";

const Index = () => {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="container mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* ML Prediction Interface */}
          <div className="lg:col-span-2">
            <MLPredictionInterface />
          </div>
          
          {/* Chatbot */}
          <div className="lg:col-span-1">
            <div className="h-full min-h-[600px]">
              <ChatBot />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;