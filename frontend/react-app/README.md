Quick React scaffold (Vite)

Getting started

1. From `frontend/react-app` run:

```bash
npm install
npm run dev
```

2. App will run at http://localhost:5173 by default.

Build for production:

```bash
npm run build
npm run preview
```

Next steps

- Migrate other pages/components from `frontend/index.html` into `src/pages` and `src/components`.
 - Migrate other pages/components from `frontend/index.html` into `src/pages` and `src/components`.
 - Wire up `VITE_API_ORIGIN` in `.env` when calling backend services.
	 - Example (development / local Docker): create `frontend/react-app/.env` with:

		 VITE_API_ORIGIN=http://localhost:8080

		 This points the frontend to the API gateway exposed at port 8080. The frontend will call endpoints like `GET ${VITE_API_ORIGIN}/api/products`.
 - Update `frontend/Dockerfile` to build the app and serve `dist/` with nginx.
