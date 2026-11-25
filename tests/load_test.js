import http from 'k6/http';
import { check, sleep } from 'k6';

// 1. Configuration
export const options = {
  // 1 user, 1 iteration (The for loop inside will send all 20 prompts sequentially)
  vus: 1,
  iterations: 1,

  // Production thresholds: Fail the test if P95 latency > 12s or error rate > 1%
  thresholds: {
    http_req_duration: ['p(95)<12000'],
    http_req_failed: ['rate<0.01'],
  },
};

// 2. Test Data (20 UNIQUE questions)
const prompts = [
  "What are the harmful effects of excessive irrigation?",
  "Tell me which vegetable consumes the most water, and which one consumes the least.",
  "How much water for tomato need per day and per season",
  "Yellow spots on tomato leaves — what is it?",
  "How often should I irrigate corn?",
  "What is the difference between early blight and late blight in tomatoes?",
  "How do I fix nitrogen deficiency in sandy soil?",
  "What crop coefficient should I use for potatoes in mid-season?",
  "Why are my onion leaves turning yellow at the tips?",
  "How does soil salinity affect water uptake in crops?",
  "What is the best irrigation method for zucchini?",
  "How does a cover crop improve soil structure?",
  "What are the symptoms of magnesium deficiency in pepper plants?",
  "How much water does a mature olive tree need?",
  "Can I use drip irrigation on lettuce?",
  "What causes damping-off in carrot seedlings?",
  "How does compaction affect root depth and yield?",
  "What is the water demand for bananas during fruiting?",
  "How do I prevent powdery mildew on zucchini?",
  "What is the seasonal water requirement for avocado?"
];

const API_URL = 'http://localhost:8000/chat';

export default function () {
  // Loop through ALL 20 prompts sequentially
  for (let i = 0; i < prompts.length; i++) {
    const uniquePrompt = prompts[i];

    // Generate a unique UUID thread_id per request so history doesn't bloat
    const threadId = crypto.randomUUID
      ? crypto.randomUUID()
      : `${__VU}-${__ITER}-${i}-${Date.now()}`;

    // Construct the payload matching your FastAPI schema
    const payload = JSON.stringify({
      question: uniquePrompt,
      thread_id: threadId
    });

    const params = {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: '30s',
    };

    // Send the request
    const response = http.post(API_URL, payload, params);

    // Validate the response
    check(response, {
      'is status 200': (r) => r.status === 200,
      'has response field': (r) => r.status === 200 && r.json('response') !== undefined,
      'is success': (r) => r.status === 200 && r.json('status') === 'success',
    });

    // Wait 1 second before the next request
    sleep(1);
  }
}
