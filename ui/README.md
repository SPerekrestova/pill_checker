## Overview

This is a cross-platform mobile and web application built with Expo and React Native. It serves as the frontend for the PillChecker ecosystem by allowing users to capture images of medications and view recognition results. The app is designed to run seamlessly on Android, iOS, and web platforms while interfacing with backend services that perform OCR and active ingredient recognition.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Installing and Running Locally](#installing-and-running-locally)
- [Docker Setup](#docker-setup)

## Features

1. **Medication Recognition Interface**
   - User-friendly UI for capturing images and initiating recognition.
   - Supports image scanning and displays results retrieved from backend services.
2. **Cross-Platform Support**
   - Built with Expo for native performance on Android, iOS, and the web.
3. **Seamless Navigation**
   - Uses Expo Router for intuitive, multi-screen navigation.
4. **State Management and API Integration**
   - Utilizes libraries like Zustand and React Query to manage state and handle API data.
5. **Docker Support**
   - Provides Docker configurations for a consistent, reproducible development environment.

## Project Structure

```
medsrecognition-frontend/
├── .husky/                # Husky configuration for Git hooks
├── node_modules/          # Installed dependencies
├── package.json           # Project metadata and scripts
├── app/                   # Main application source (screens, components, navigation)
├── assets/                # Static assets (images, fonts, etc.)
├── entities/              # Domain models or entities used across features
├── features/              # Feature modules containing related logic and UI elements
├── pages/                 # Page or screen components (if using a pages-based approach)
├── shared/                # Shared utilities, hooks, components, or constants
├── .gitignore             # Git ignore rules
├── .prettierignore        # Prettier ignore rules
├── prettierrc             # Prettier configuration
├── app.json               # Expo configuration
├── babel.config.json      # Babel configuration
├── eslint.config.mjs      # ESLint configuration (module format)
├── tsconfig.json          # TypeScript configuration
├── Dockerfile             # Docker instructions for containerization
├── docker-compose.yml     # Docker Compose file for multi-container setups
└── .dockerignore          # Files and directories to ignore during Docker builds
```

## Prerequisites

- **Node.js** (LTS version recommended)
- **Expo CLI**: Install globally via `npm install -g expo-cli`
- **Yarn** or **npm** for package management
- **Docker** (optional, for containerized development)

## Environment Variables

The app may require environment variables for configuration (such as API endpoints or public keys). Create a `.env` file in the project root:

```env
# Example .env.local file
API_URL=https://api.example.com
SENTRY_AUTH_TOKEN=your_auth_key
```

> **Note:** Do not commit sensitive values in your `.env` file.

## Installing and Running Locally

1. **Clone the Repository**

   ```bash
   git clone https://github.com/SPerekrestova/medsrecognition-frontend.git
   cd medsrecognition-frontend
   ```

2. **Install Dependencies**

   ```bash
   npm install
   # or using Yarn:
   yarn install
   ```

3. **Start the Expo Development Server**

   To launch the development server:

   ```bash
   npm start
   # or for platform-specific commands:
   npm run android
   npm run ios
   npm run web
   ```

   Follow the on-screen instructions to open the app on your device, simulator, or browser.

## Docker Setup

For a consistent development environment or to simplify deployment, you can run the app inside Docker.

### Running with Docker

1. **Build the Docker Image**

   ```bash
   docker build -t medsrecognition-frontend .
   ```

2. **Run the Container**

   ```bash
   docker run -it -p 19000:19000 -p 19001:19001 -p 19002:19002 medsrecognition-frontend
   ```

   _Alternatively, using Docker Compose:_

   ```bash
   docker-compose up
   ```
