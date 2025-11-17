/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#667eea',
                secondary: '#764ba2',
            },
            animation: {
                'pulse-delay-75': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite 75ms',
                'pulse-delay-150': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite 150ms',
            }
        },
    },
    plugins: [],
}
