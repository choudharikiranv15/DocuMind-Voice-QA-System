import posthog from 'posthog-js';

let posthogInitialized = false;

export const initPostHog = () => {
  const apiKey = import.meta.env.VITE_POSTHOG_API_KEY;
  const host = import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com';

  // Silently skip if not configured (expected in development)
  if (!apiKey || apiKey === 'your_posthog_key_here') {
    return false;
  }

  try {
    posthog.init(apiKey, {
      api_host: host,
      loaded: (posthog) => {
        if (import.meta.env.MODE === 'development') {
          posthog.opt_out_capturing(); // Don't track in development
        }
      },
    });

    posthogInitialized = true;
    if (import.meta.env.DEV) console.log('✅ PostHog initialized');
    return true;
  } catch (error) {
    // Error logged server-side only - silent failure for tracking service
    return false;
  }
};

export const identifyUser = (userId, properties = {}) => {
  if (posthogInitialized) {
    posthog.identify(userId, properties);
  }
};

export const trackEvent = (eventName, properties = {}) => {
  if (posthogInitialized) {
    posthog.capture(eventName, properties);
  }
};

export const trackPageView = () => {
  if (posthogInitialized) {
    posthog.capture('$pageview');
  }
};

// Specific event tracking functions
export const analytics = {
  signup: (userId, role) => {
    trackEvent('user_signup', { role });
    identifyUser(userId, { role, signup_date: new Date().toISOString() });
  },

  login: (userId) => {
    trackEvent('user_login');
  },

  documentUpload: (filename, fileSize) => {
    trackEvent('document_upload', { filename, file_size: fileSize });
  },

  query: (queryType, queryLength) => {
    trackEvent('query_asked', { query_type: queryType, query_length: queryLength });
  },

  feedback: (rating, hasComment) => {
    trackEvent('feedback_submitted', { rating, has_comment: hasComment });
  },

  voiceRecording: (duration) => {
    trackEvent('voice_recording', { duration });
  },

  ttsGenerated: () => {
    trackEvent('tts_generated');
  },
};

export default analytics;
