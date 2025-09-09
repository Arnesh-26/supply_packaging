import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const App = () => {
  const [chatInput, setChatInput] = useState("");
  const [chatReply, setChatReply] = useState("");
  const [prediction, setPrediction] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Prediction input states
  const [date, setDate] = useState("");
  const [temperature, setTemperature] = useState<number | "">("");
  const [humidity, setHumidity] = useState<number | "">("");
  const [transportationTime, setTransportationTime] = useState<number | "">("");

  // Call backend /chat
  const sendChat = async () => {
    const res = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: chatInput }),
    });
    const data = await res.json();
    setChatReply(data.reply);
  };

  // Call backend /predict
  const sendPrediction = async () => {
    const res = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date,
        temperature,
        humidity,
        transportation_time: transportationTime,
      }),
    });
    const data = await res.json();
    setPrediction(data);
    setShowDetails(false); // reset details view each time
  };

  return (
    <div className="p-6 text-center">
      <h1 className="text-2xl font-bold mb-6">ML Packaging Predictor</h1>

      {/* Chatbot */}
      <div className="mb-10">
        <h2 className="text-xl mb-2">Chatbot</h2>
        <input
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask about packaging..."
          className="border rounded p-2 w-1/2 text-blue-600"
        />
        <button
          onClick={sendChat}
          className="ml-2 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Ask
        </button>

        <AnimatePresence>
          {chatReply && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="mt-4 max-w-xl mx-auto p-4 rounded-2xl bg-blue-50 border border-blue-200 shadow"
            >
              <h3 className="text-lg font-semibold text-blue-700 mb-2">
                Chatbot Reply
              </h3>
              <p className="text-gray-800">{chatReply}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Prediction */}
      <div>
        <h2 className="text-xl mb-2">Prediction</h2>

        <div className="space-y-2 mb-4">
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="border rounded p-2 w-1/2 text-green-600"
          />
          <input
            type="number"
            placeholder="Temperature"
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
            className="border rounded p-2 w-1/2 text-green-600"
          />
          <input
            type="number"
            placeholder="Humidity"
            value={humidity}
            onChange={(e) => setHumidity(Number(e.target.value))}
            className="border rounded p-2 w-1/2 text-green-600"
          />
          <input
            type="number"
            placeholder="Transportation Time"
            value={transportationTime}
            onChange={(e) => setTransportationTime(Number(e.target.value))}
            className="border rounded p-2 w-1/2 text-green-600"
          />
        </div>

        <button
          onClick={sendPrediction}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Get Prediction
        </button>

        {/* Enhanced Prediction Output */}
        <AnimatePresence>
          {prediction && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="mt-6 max-w-xl mx-auto p-4 rounded-2xl bg-green-50 border border-green-200 shadow"
            >
              <h3 className="text-lg font-semibold text-green-700 mb-3">
                Prediction Result
              </h3>

              <div className="grid grid-cols-2 gap-4 text-left">
                <div>
                  <p className="text-sm text-gray-500">Predicted Class</p>
                  <p className="text-xl font-bold text-green-700">
                    {prediction.prediction}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Plastic Probability</p>
                  <p className="text-xl font-bold text-green-700">
                    {prediction.probability_plastic}
                  </p>
                </div>
              </div>

              {/* Toggle Button for Extra Details */}
              <div className="mt-4">
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="px-3 py-2 text-sm bg-gray-200 hover:bg-gray-300 rounded"
                >
                  {showDetails ? "Hide Details" : "Show Details"}
                </button>

                <AnimatePresence>
                  {showDetails && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      transition={{ duration: 0.3 }}
                      className="mt-3 bg-white rounded-lg p-3 text-gray-700 shadow-inner"
                    >
                      <pre className="text-sm whitespace-pre-wrap">
                        {JSON.stringify(prediction.features, null, 2)}
                      </pre>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default App;
