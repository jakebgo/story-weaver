# Work Plan: [Tool Name Placeholder - e.g., Story Weaver] MVP 


**Document Purpose:** This document provides a comprehensive work plan and context for the Cursor AI Agent tasked with building the Minimum Viable Product (MVP) of the "[Tool Name Placeholder - e.g., Story Weaver]" application. Follow the phases and instructions detailed below precisely.


**1. Overall Project Goal:**
To deliver an MVP application that helps writers' rooms by automatically transcribing recorded discussions, using AI to analyze the transcript and generate a structured story outline/beat sheet with links back to the relevant transcript context. The focus is on the automated workflow, core usability (especially transcript correction), and adherence to the specified technology stack within free-tier limitations.


**2. Core Workflow Overview:**
1.  **Authentication:** User signs up or logs in securely using Email/Password (via Firebase Auth).
2.  **Recording:** Authenticated user starts and stops an audio recording session within the web application.
3.  **AI Processing (Backend):**
    *   Audio is sent securely to the backend.
    *   Backend uses a chosen Transcription API (e.g., Gladia) to transcribe the audio, requesting speaker labels and timestamps.
    *   The transcript text is chunked.
    *   Each chunk is embedded using a local Sentence-BERT model.
    *   Embeddings, text chunks, and metadata (including segment identifiers) are stored in Qdrant Cloud (Vector DB).
    *   Using LlamaIndex, the backend performs Retrieval-Augmented Generation (RAG): retrieves relevant chunks from Qdrant based on analysis needs.
    *   Backend uses the Gemini API (via LlamaIndex) with engineered prompts to analyze retrieved chunks for:
        *   Key Topics/Narrative Beats (FR-A4)
        *   Key Moments (Decisions/Questions) (FR-A5)
        *   Key Terms (FR-A6)
    *   Backend uses Gemini API (via LlamaIndex RAG) with a final refined prompt to generate a structured outline/beat sheet, embedding references (segment IDs/timestamps) to the source transcript segments (FR-A7, FR-A8).
4.  **Output Delivery (Frontend):**
    *   The application displays the full, speaker-labeled transcript in an editable interface (FR-A3).
    *   The application displays the AI-generated structured outline (FR-A9).
    *   Outline elements contain clickable links that scroll/highlight the corresponding section in the transcript view (FR-A10).
    *   User can export the generated outline to Text and DOCX formats (FR-A12).
    *   (If implemented) Basic keyword search across transcript/outline (FR-A11 [S]).


**3. Technology Stack:**
*   **Frontend:** React (using Vite recommended), JavaScript/TypeScript
*   **Backend:** Python (using Flask/FastAPI or a Serverless framework like Chalice/AWS Lambda/Google Cloud Functions suitable for free tier hosting)
*   **Authentication:** Firebase Authentication (Spark Plan - Free Tier)
*   **Transcription API:** Chosen provider like Gladia API (Free Tier) or AssemblyAI/Deepgram (Free Credits) - *Requires validation*
*   **LLM:** Google Gemini Flash/Pro API (Free Tier), potentially OpenRouter (Free Tier - e.g., Mistral 7B) as secondary/fallback.
*   **Embedding:** Local Sentence-BERT model (via `transformers` library in Python backend)
*   **Vector Database:** Qdrant Cloud (Free Tier)
*   **AI Orchestration:** LlamaIndex (Python library)
*   **Outline Export (DOCX):** `mammoth` or `docx` JavaScript library (client-side)
*   **Frontend Hosting:** Netlify (Free Tier) or Firebase Hosting
*   **Backend Hosting:** Suitable Free Tier service (e.g., Render, Google Cloud Run, Vercel Serverless Functions) capable of running Python/Docker and local embedding models.


**4. Phased Implementation Plan:**


**Phase 1: Core Technology Integration & Pipeline Proof-of-Concept (Focus: Prove API integrations & basic end-to-end flow)**
*Objective: Establish foundational project structures, integrate core external APIs, set up the embedding process, and verify a basic data flow from audio input to initial AI-generated outline display.*


*   **Task 1.1: Project Setup**
    *   Initialize React frontend project (use Vite).
    *   Initialize Python backend project (choose framework suitable for target host, e.g., Flask/FastAPI/Chalice).
    *   Set up Git repository with standard frontend/backend structure.
*   **Task 1.2: Authentication Setup (TC2, FR-Auth1, NFR-Auth)**
    *   Configure Firebase project (Spark Plan), enable Email/Password Authentication.
    *   Frontend: Integrate Firebase JS SDK. Implement basic Login/Signup UI components and authentication flow logic (handle token refresh).
    *   Backend: Integrate Firebase Admin SDK. Implement middleware/decorator to verify Firebase ID Token signature and claims on *all* authenticated API routes. Return 401/403 errors if invalid.
*   **Task 1.3: Backend Foundation & Deployment Setup (TC1, TC3)**
    *   Set up basic backend server/serverless function structure.
    *   *Directive:* Implement secure handling for ALL API keys/secrets using environment variables or a secrets management service. **Do not commit secrets to Git.**
    *   Configure initial deployment target for backend (e.g., Render free tier).
*   **Task 1.4: Transcription API Integration (FR-A2, NFR-T1 partial)**
    *   Backend: Implement endpoint to receive audio data (e.g., Blob/FormData) from authenticated frontend requests.
    *   Backend: Integrate the chosen Transcription API's Python SDK/client.
    *   Backend: Implement function to call transcription API, explicitly requesting speaker labels and timestamps.
    *   Backend: *Directive:* Implement robust handling for asynchronous results (polling mechanism recommended for MVP). Handle API errors gracefully (rate limits, invalid audio, API downtime). Log API calls/responses for debugging.
    *   Backend: Return raw transcript data (text, speakers, timestamps) to frontend upon completion.
*   **Task 1.5: Embedding & Vector DB Setup (TC4 Dependencies)**
    *   Setup: Create Qdrant Cloud free tier cluster, obtain API key.
    *   Backend: Configure Qdrant Python client.
    *   Backend: Set up environment for local Sentence-BERT (`transformers` library). *Directive:* Be mindful of backend host resource limits (CPU/RAM) for embedding; consider if async processing is needed later. Test basic embedding generation.
    *   Backend: Implement basic LlamaIndex pipeline components: `SimpleDirectoryReader` (or equivalent for in-memory text), `SentenceSplitter` (chunking), configured local Embedder (Sentence-BERT), Qdrant Vector Store.
    *   Backend: Implement logic to: Load transcript -> Chunk text -> Generate embeddings -> Store embeddings, text chunks, and necessary metadata (unique segment IDs, potentially user ID) in Qdrant.
    *   Test: Verify successful embedding and storage in Qdrant.
*   **Task 1.6: Basic AI Outline Generation PoC (FR-A7 initial)**
    *   Backend: Integrate Gemini API Python client/SDK.
    *   Backend: Implement basic LlamaIndex RAG query logic: Define a `VectorIndexRetriever` for Qdrant -> Define a basic `ResponseSynthesizer` using the Gemini LLM.
    *   Backend: Implement function to execute RAG query with a simple test prompt (e.g., "Summarize this session").
    *   Test: Verify successful LLM call using retrieved context from Qdrant and generation of some structured text output. Handle potential LLM API errors/rate limits.
*   **Task 1.7: Basic Frontend Display (FR-A1 basic, FR-A9 initial)**
    *   Frontend: Implement basic audio recording UI using Web Audio API, sending recorded Blob to backend.
    *   Frontend: Implement simple UI components to display the raw transcript and raw AI-generated outline fetched from backend polling endpoint(s).
    *   Frontend: Implement basic UI flow: Login -> Show Recording Button -> Record Audio -> Send to Backend -> Poll for/Display Transcript & Outline.
*   **Phase 1 Goal Check:** Verify: User can log in, record audio, send it to backend, backend processes via Transcription API -> Chunk/Embed/Store -> Basic RAG/LLM call, and frontend displays the raw transcript and a raw AI outline. All external services (Firebase Auth, Transcription, Qdrant, Gemini) are connected and functioning at a basic level.


**Phase 2: Core Functionality & Usability (Focus: Build the essential interactive loop & make output usable)**
*Objective: Build the critical UIs for transcript correction and outline navigation. Implement the specific AI analysis prompts. Make the core workflow functional and usable.*


*   **Task 2.1: Transcript Correction UI (FR-A3, NFR-U3, UX-C1)**
    *   Frontend: *Directive:* Develop an efficient, user-friendly React component for displaying the transcript with speaker labels. This component MUST allow easy inline editing of the transcript text content and speaker label assignments. This is CRITICAL for overall usability (NFR-T1 mitigation).
    *   Frontend: Implement state management to hold the corrected transcript data.
    *   Backend (Optional/Simple): Implement a simple backend endpoint to persist corrected transcript text if needed beyond client-side state for this phase (consider simple storage, maybe update Qdrant metadata or a simple DB record).
*   **Task 2.2: Refined AI Analysis Prompts (FR-A4, FR-A5, FR-A6)**
    *   Backend: Within the LlamaIndex pipeline (or separate calls if easier), implement specific LLM calls using RAG context.
    *   *Directive:* Engineer and iterate on specific prompts for the Gemini LLM to explicitly request detection/extraction of:
        *   Key Topics/Narrative Beats (FR-A4)
        *   Key Moments (Decisions/Questions) (FR-A5)
        *   Key Terms (FR-A6)
    *   Consider how to structure these calls (e.g., multiple parallel queries, single complex query).
*   **Task 2.3: Refined Outline Generation & Linking Data (FR-A7, FR-A8, NFR-O1)**
    *   Backend: Refine the final LlamaIndex RAG query/prompt for outline generation (FR-A7). Use insights/outputs from Task 2.2 to inform this prompt.
    *   *Directive:* CRITICAL: Update the prompt to explicitly instruct the LLM to include source transcript segment references (the unique segment IDs/metadata stored in Qdrant during Task 1.5) alongside each generated outline point/beat.
    *   *Directive:* Implement robust parsing logic for the LLM's response to reliably extract both the hierarchical outline structure AND the associated source segment references for each point. Store this structured data (outline + references) for frontend retrieval.
*   **Task 2.4: Clickable Outline -> Transcript Linking (FR-A10, UX-L1)**
    *   Frontend: Update the UI component displaying the AI-generated outline (from Task 2.3).
    *   Frontend: *Directive:* Make outline elements (or embedded reference markers) clickable.
    *   Frontend: Implement logic that uses the source segment references associated with a clicked outline item to scroll to and visually highlight the corresponding segment(s) in the **corrected** transcript display component (from Task 2.1).
*   **Task 2.5: Basic Error Handling & Backend Refinement**
    *   Backend/Frontend: Implement more robust error handling across the entire workflow (API call failures, embedding issues, LLM timeouts, parsing errors). Provide informative feedback to the user.
    *   Backend: Refine backend code structure for better organization, modularity, and logging.
*   **Phase 2 Goal Check:** Verify: User can effectively correct the transcript. The AI pipeline generates a more structured outline informed by specific analysis prompts, and this outline includes parseable source references. Clicking outline items reliably navigates the corrected transcript view. The core interactive loop is functional.


**Phase 3: Output, Polish & Deployment Readiness (Focus: Complete workflow & prepare for validation)**
*Objective: Finalize output features, implement deferred 'Should Haves' (if applicable), refine usability/performance, test thoroughly, and prepare for deployment.*


*   **Task 3.1: Outline Export (FR-A12)**
    *   Frontend: Implement client-side JavaScript logic for "Export as Plain Text".
    *   Frontend: Integrate `mammoth` or `docx` JS library.
    *   Frontend: Implement logic to take the structured outline data (from Task 2.3) and format it correctly for DOCX generation. Trigger file download.
*   **Task 3.2: Keyword Search (FR-A11 [S])**
    *   *Directive:* Implement this "Should Have" feature if time permits and core features are stable.
    *   Frontend: Integrate a client-side search library (e.g., `Fuse.js`).
    *   Frontend: Implement a search input and logic to search across the text content of both the (corrected) transcript display and the outline display components, highlighting matches.
*   **Task 3.3: Performance & Reliability Tuning (NFR-A1, NFR-R1, NFR-API Limits)**
    *   Frontend: Optimize rendering performance, especially the transcript editor and potentially large outline lists.
    *   Backend: Review AI pipeline execution time (NFR-A1 target < 5-10 mins). Identify and address bottlenecks (e.g., slow embedding if synchronous, inefficient Qdrant queries, slow LLM calls).
    *   *Directive:* Review API usage patterns against free tier limits (NFR-API Limits). Implement basic logging or checks if feasible.
    *   Testing: Test data integrity scenarios (e.g., ensure user outputs are associated correctly, partial processing failures).
*   **Task 3.4: UI/UX Polish (UX-O1, UX-L1, UX-C1)**
    *   Frontend: Refine overall application layout, CSS styling, and responsiveness for standard screen sizes.
    *   Frontend: Improve clarity of UI elements, button labels, loading indicators, and user feedback messages (errors, success).
    *   Frontend: Ensure the transcript correction (UX-C1) and outline linking (UX-L1) interactions feel smooth and intuitive.
*   **Task 3.5: Testing & Bug Fixing (TC5)**
    *   Conduct thorough end-to-end testing of the complete workflow with various audio samples (different lengths, accents, noise levels).
    *   Specifically test the transcript correction flow and its impact on linking accuracy.
    *   Evaluate the quality and usefulness of the generated outlines (NFR-O1).
    *   Test across latest versions of major browsers (Chrome, Firefox, Safari, Edge).
    *   Address all critical and major bugs identified.
*   **Task 3.6: Deployment & Configuration (TC1, TC3, NFR-R2)**
    *   Finalize deployment configurations and build scripts for frontend (Netlify/Firebase Hosting) and backend (chosen host).
    *   *Directive:* Ensure all API keys, database credentials, and other secrets are configured securely in the production environment settings (using environment variables). **Verify no secrets are in the codebase.**
    *   Set up basic uptime monitoring for backend and frontend URLs (NFR-R2).
*   **Phase 3 Goal Check:** Verify: The complete MVP workflow is functional, performs reasonably well, and is usable. Outline export works correctly. Keyword search [S] is functional if implemented. The application is deployed to production hosts and basic monitoring is in place. Ready for initial user validation.


**5. Key Implementation Directives (Summary):**
*   **Security (TC3, NFR-Auth):** Prioritize security. Handle API keys securely on the backend ONLY (env vars/secrets manager). Rigorously verify Firebase ID Tokens on every authenticated backend request. Use HTTPS. Perform basic input validation.
*   **Error Handling:** Implement robust error handling and user feedback for all external API calls (Transcription, LLM, Qdrant) and internal processing steps (embedding, parsing).
*   **API Limits (NFR-API Limits):** Code defensively and monitor usage against the free tiers of all integrated services. This is critical for MVP viability.
*   **Transcript Correction (FR-A3):** This UI is CRITICAL. Invest time in making it efficient and usable.
*   **Outline Linking Data (FR-A8):** Ensuring the LLM reliably outputs usable source references AND that the backend correctly parses them is crucial for the core linking feature (FR-A10).
*   **Prompt Engineering:** Expect iteration on prompts for FR-A4, FR-A5, FR-A6, and FR-A7 to achieve acceptable quality (NFR-O1). Allow for experimentation.
*   **Asynchronous Operations:** Handle the asynchronous nature of transcription (and potentially embedding/LLM calls) correctly using polling or webhooks (polling preferred for MVP simplicity).
*   **Local Embedding Resources:** Monitor resource usage of the local Sentence-BERT model on the chosen backend hosting tier.


**6. Core Requirements Summary (MoSCoW - Must Haves [M], Should Have [S]):**
*   **Functional Requirements (FR):**
    *   [M] FR-Auth1: User Sign-up/Login (Firebase Email/Password).
    *   [M] FR-A1: Allow audio recording.
    *   [M] FR-A2: Auto-transcribe via API (speaker labels, timestamps).
    *   [M] FR-A3: Efficient UI for transcript correction (text & speakers).
    *   [M] FR-A4: AI Analysis - Key Topics/Beats.
    *   [M] FR-A5: AI Analysis - Key Moments.
    *   [M] FR-A6: AI Analysis - Key Terms.
    *   [M] FR-A7: AI Outline Generation (structured).
    *   [M] FR-A8: AI Context Linking (embed transcript refs in outline).
    *   [M] FR-A9: Display Outline & Transcript clearly.
    *   [M] FR-A10: Clickable Outline links to Transcript section.
    *   [S] FR-A11: Basic keyword search (outline/transcript).
    *   [M] FR-A12: Export outline (Plain Text, DOCX).
*   **Non-Functional Requirements (NFR):**
    *   [M] NFR-T1: Usable Transcription Accuracy (API + Correction UI).
    *   [M] NFR-A1: Reasonable AI Analysis Performance (< 5-10 min target).
    *   [M] NFR-O1: Coherent & Useful AI Outline Quality.
    *   [M] NFR-R1: Data Integrity (prevent loss).
    *   [M] NFR-R2: Baseline Uptime.
    *   [M] NFR-R3: Basic Backup strategy (inherent in some services).
    *   [M] NFR-U1: Clear & Navigable Output Usability.
    *   [M] NFR-API Limits: Stay within ALL free tier limits.
    *   [M] NFR-Auth: Secure Firebase Token handling.
*   **Technical Constraints (TC):**
    *   [M] TC1: SaaS Deployment (Netlify/Firebase + Free Tier Backend).
    *   [M] TC2: Use Firebase Authentication (Spark Plan).
    *   [M] TC3: Foundational Security Practices.
    *   [M] TC4: Dependency on specified APIs/Libs (Transcription, LLM, Qdrant, LlamaIndex, Sentence-BERT).
    *   [M] TC5: Standard Browser Support.
    *   [M] TC6: React Frontend, Python Backend.
*   **User Experience Requirements (UX):**
    *   [M] UX-S1: Simple Recording Flow.
    *   [M] UX-O1: Clear Output Presentation.
    *   [M] UX-L1: Reliable & Useful Linking.
    *   [M] UX-C1: Efficient Transcript Correction.


**7. Key Exclusions (Not in MVP):**
*   NO Manual Mapping/Visual Canvas features (React Flow integration is OUT).
*   NO Real-time AI analysis during recording.
*   NO Advanced AI features (e.g., sophisticated summarization, trend analysis, suggestion generation).
*   NO Versioning or branching of outlines/transcripts.
*   NO Manual metadata tagging by users.
*   NO Advanced search/filtering capabilities (beyond basic keyword if FR-A11 included).
*   NO Synchronized audio playback linked to text highlighting.
*   NO Enterprise features (SSO, advanced permissions, user roles).
*   NO Deep integrations with external writing software (e.g., Final Draft).
*   NO High scalability optimizations beyond free tier capabilities.


**8. Prerequisites (Required Before Starting Phase 1):**
*   Access to a configured Firebase Project (Spark Plan) with Email/Password Auth enabled. Obtain Firebase SDK configuration details.
*   Google Cloud Project with Gemini API enabled OR Google AI Studio access. Obtain Gemini API Key.
*   Account with the chosen Transcription Service (e.g., Gladia, AssemblyAI, Deepgram). Obtain API Key.
*   Qdrant Cloud account with a free tier cluster set up. Obtain Cluster URL and API Key.
*   (Optional but Recommended) OpenRouter.ai account and API Key for accessing alternative LLMs.


**Proceed with Phase 1, following the tasks and directives outlined above.**

