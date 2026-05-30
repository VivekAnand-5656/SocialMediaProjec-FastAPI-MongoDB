Social Media Web Application

This is a full-stack Social Media Web Project where users can create an account, interact with posts, and connect with other users through follow-based networking.

🚀 Features
User Authentication (Register / Login)
Create, Update, and Delete Posts (CRUD operations)
Like / Unlike Posts
Comment on Posts
Follow / Unfollow Users
Update User Profile
Secure API-based backend
🗄️ Database Design

The project uses MongoDB Atlas as the database.

It contains two main collections:

👤 Users Collection

Stores user-related information such as:

User profile details
Authentication data
Followers / Following data
📝 Posts Collection

Stores post-related data such as:

Post content (caption, image, etc.)
Likes and comments
User reference (author of post)

Relationships between users and posts are handled using MongoDB references (ObjectId).

🛠️ Tech Stack
Backend: Python, FastAPI
Database: MongoDB Atlas
Media Storage: Cloudinary (for image uploads)
API Testing: Swagger UI (FastAPI built-in)
 
💡 Project Goal

This project was built to understand and implement real-world backend concepts like authentication, database relationships, and RESTful API design using modern Python frameworks.