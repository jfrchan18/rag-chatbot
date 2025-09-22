# RAG Chatbot React Frontend

A modern React frontend for the RAG (Retrieval-Augmented Generation) Chatbot application.

## Features

- **Modern React Architecture**: Built with React 18 and functional components with hooks
- **Component-based Design**: Modular components for better maintainability
- **Responsive UI**: Mobile-friendly design with CSS Grid and Flexbox
- **Real-time Chat**: Interactive chat interface with typing indicators
- **PDF Upload**: Drag-and-drop PDF file upload functionality
- **Export Chat**: Export conversation history as text file
- **Error Handling**: Comprehensive error handling and user feedback

## Components

- `App.js` - Main application component with state management
- `Header.js` - Top navigation bar with action buttons
- `UploadSection.js` - PDF file upload interface
- `Chat.js` - Chat messages container
- `MessageBubble.js` - Individual message display component
- `Composer.js` - Message input and send functionality
- `ErrorMessage.js` - Error display component

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the react-frontend directory:
   ```bash
   cd react-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This will create a `dist` folder with the production build.

## API Integration

The React frontend connects to the FastAPI backend running on `http://localhost:8000`. Make sure the backend is running before starting the frontend.

### API Endpoints Used

- `POST /ask` - Send chat messages
- `POST /upload-pdf` - Upload PDF documents

## Styling

The application uses CSS custom properties (CSS variables) for theming and responsive design. The styles are organized into:

- `index.css` - Global styles and CSS variables
- `App.css` - Component-specific styles

## Development

The project uses Webpack for bundling and includes:

- Babel for JavaScript/JSX transpilation
- CSS Loader for stylesheet processing
- Hot Module Replacement for development
- HTML Webpack Plugin for HTML generation

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT License
