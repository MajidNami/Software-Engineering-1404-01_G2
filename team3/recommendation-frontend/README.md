\# Recommendation Service - Frontend



\## 📌 Project Description

This is the \*\*Front-end application\*\* for the Recommendation Service, developed as part of \*\*Phase 7\*\* of the Software Engineering course project.



The application is responsible for displaying recommendation results received from the \*\*Core Service\*\*.



---



\## 🧩 Responsibilities

\- Display recommendation scenarios

\- Show recommendation list with reasons

\- Handle UI states:

&nbsp; - Loading

&nbsp; - Error

&nbsp; - Empty state

\- Connect \*\*only to Core API\*\* (not directly to Recommendation Service)



---



\## ⚙️ Technologies Used

\- React

\- Vite

\- Axios

\- JavaScript (ES6)



---



\## 🔗 API Integration

The frontend communicates with the Core Service using the following endpoint:

```http

GET /api/recommendations

Requests are sent with `withCredentials: true` for authentication.



