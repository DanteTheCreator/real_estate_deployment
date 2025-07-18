# Real Estate Rental API Documentation

## Overview

The Real Estate Rental API is a comprehensive backend service for managing property rentals, built with FastAPI. It provides endpoints for user authentication, property management, image handling through MinIO, and rental application processing.

**Base URL:** `http://localhost:8000`  
**Documentation:** `http://localhost:8000/docs` (Swagger UI)  
**Alternative Docs:** `http://localhost:8000/redoc` (ReDoc)

## Table of Contents

1. [Authentication](#authentication)
2. [Properties](#properties)
3. [Property Images](#property-images)
4. [Rental Applications](#rental-applications)
5. [Amenities](#amenities)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)
8. [MinIO Integration](#minio-integration)

---

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Register User
**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "tenant"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "tenant",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-07-15T19:30:00Z"
  }
}
```

### Login
**POST** `/api/auth/login`

Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "tenant",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-07-15T19:30:00Z"
  }
}
```

### Get Current User
**GET** `/api/auth/me`

Get information about the currently authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "tenant",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-07-15T19:30:00Z"
}
```

### Update User Profile
**PUT** `/api/auth/me`

Update current user's profile information.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1987654321"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1987654321",
  "role": "tenant",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-07-15T19:30:00Z"
}
```

---

## Properties

### Get All Properties
**GET** `/api/properties/`

Retrieve a list of available properties with optional filtering.

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 10, max: 100): Number of records to return
- `city` (string): Filter by city name
- `state` (string): Filter by state
- `property_type` (string): Filter by property type (apartment, house, condo, townhouse, studio)
- `min_rent` (float): Minimum rent amount
- `max_rent` (float): Maximum rent amount
- `min_bedrooms` (int): Minimum number of bedrooms
- `max_bedrooms` (int): Maximum number of bedrooms
- `pets_allowed` (boolean): Filter by pet policy
- `is_furnished` (boolean): Filter by furnished status

**Example Request:**
```
GET /api/properties/?city=Dallas&min_rent=1000&max_rent=3000&pets_allowed=true
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "2 Bed 2.5 Bath Apartment in Dallas",
    "address": "123 Main St",
    "city": "Dallas",
    "state": "TX",
    "zip_code": "75201",
    "property_type": "apartment",
    "bedrooms": 2,
    "bathrooms": 2.5,
    "rent_amount": 2500.0,
    "is_available": true,
    "created_at": "2025-07-15T19:30:00Z",
    "images": [
      {
        "id": 16,
        "property_id": 1,
        "image_url": "http://127.0.0.1:9000/real-estate/30600318.png",
        "caption": "Property image - 30600318.png",
        "is_primary": true,
        "order_index": 0,
        "created_at": "2025-07-15T23:37:59Z"
      }
    ]
  }
]
```

### Get Property by ID
**GET** `/api/properties/{property_id}`

Get detailed information about a specific property.

**Path Parameters:**
- `property_id` (int): The property ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "2 Bed 2.5 Bath Apartment in Dallas",
  "description": "Beautiful apartment in downtown Dallas with modern amenities",
  "address": "123 Main St",
  "city": "Dallas",
  "state": "TX",
  "zip_code": "75201",
  "country": "USA",
  "property_type": "apartment",
  "bedrooms": 2,
  "bathrooms": 2.5,
  "square_feet": 1200,
  "lot_size": null,
  "rent_amount": 2500.0,
  "security_deposit": 2500.0,
  "lease_duration": 12,
  "available_date": null,
  "is_furnished": false,
  "pets_allowed": true,
  "smoking_allowed": false,
  "year_built": 2020,
  "parking_spaces": 1,
  "utilities_included": "water, trash",
  "is_available": true,
  "owner_id": 2,
  "created_at": "2025-07-15T19:30:00Z",
  "updated_at": null,
  "images": [
    {
      "id": 16,
      "property_id": 1,
      "image_url": "http://127.0.0.1:9000/real-estate/30600318.png",
      "caption": "Property image - 30600318.png",
      "is_primary": true,
      "order_index": 0,
      "created_at": "2025-07-15T23:37:59Z"
    }
  ],
  "amenities": [
    {
      "id": 1,
      "name": "WiFi",
      "description": "High-speed internet access",
      "icon": "wifi",
      "category": "utilities"
    }
  ]
}
```

### Create Property
**POST** `/api/properties/`

Create a new property listing. Requires landlord role.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Modern Studio Apartment",
  "description": "Newly renovated studio in prime location",
  "address": "456 Oak Street",
  "city": "Austin",
  "state": "TX",
  "zip_code": "78701",
  "country": "USA",
  "property_type": "studio",
  "bedrooms": 0,
  "bathrooms": 1.0,
  "square_feet": 600,
  "rent_amount": 1800.0,
  "security_deposit": 1800.0,
  "lease_duration": 12,
  "is_furnished": true,
  "pets_allowed": false,
  "smoking_allowed": false,
  "year_built": 2023,
  "parking_spaces": 1,
  "utilities_included": "water, electricity",
  "amenity_ids": [1, 2, 3]
}
```

**Response:** `201 Created`
```json
{
  "id": 15,
  "title": "Modern Studio Apartment",
  "description": "Newly renovated studio in prime location",
  "address": "456 Oak Street",
  "city": "Austin",
  "state": "TX",
  "zip_code": "78701",
  "country": "USA",
  "property_type": "studio",
  "bedrooms": 0,
  "bathrooms": 1.0,
  "square_feet": 600,
  "lot_size": null,
  "rent_amount": 1800.0,
  "security_deposit": 1800.0,
  "lease_duration": 12,
  "available_date": null,
  "is_furnished": true,
  "pets_allowed": false,
  "smoking_allowed": false,
  "year_built": 2023,
  "parking_spaces": 1,
  "utilities_included": "water, electricity",
  "is_available": true,
  "owner_id": 2,
  "created_at": "2025-07-15T19:45:00Z",
  "updated_at": null,
  "images": [],
  "amenities": [
    {
      "id": 1,
      "name": "WiFi",
      "description": "High-speed internet access",
      "icon": "wifi",
      "category": "utilities"
    }
  ]
}
```

### Update Property
**PUT** `/api/properties/{property_id}`

Update an existing property. Must be the property owner or admin.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `property_id` (int): The property ID

**Request Body:**
```json
{
  "title": "Updated Modern Studio Apartment",
  "rent_amount": 1900.0,
  "is_available": false
}
```

**Response:** `200 OK`
```json
{
  "id": 15,
  "title": "Updated Modern Studio Apartment",
  "rent_amount": 1900.0,
  "is_available": false,
  "updated_at": "2025-07-15T20:00:00Z"
}
```

### Delete Property
**DELETE** `/api/properties/{property_id}`

Delete a property listing. Must be the property owner or admin.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `property_id` (int): The property ID

**Response:** `200 OK`
```json
{
  "message": "Property deleted successfully"
}
```

### Get User's Properties
**GET** `/api/properties/my-properties/`

Get all properties owned by the current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 10): Number of records to return

**Response:** `200 OK`
```json
[
  {
    "id": 15,
    "title": "Updated Modern Studio Apartment",
    "address": "456 Oak Street",
    "city": "Austin",
    "state": "TX",
    "zip_code": "78701",
    "property_type": "studio",
    "bedrooms": 0,
    "bathrooms": 1.0,
    "rent_amount": 1900.0,
    "is_available": false,
    "created_at": "2025-07-15T19:45:00Z",
    "images": []
  }
]
```

---

## Property Images

### Add Property Image
**POST** `/api/properties/{property_id}/images/`

Add a new image to a property. Must be the property owner.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `property_id` (int): The property ID

**Request Body:**
```json
{
  "image_url": "http://127.0.0.1:9000/real-estate/new-image.jpg",
  "caption": "Beautiful living room view",
  "is_primary": false,
  "order_index": 1
}
```

**Response:** `201 Created`
```json
{
  "id": 24,
  "property_id": 15,
  "image_url": "http://127.0.0.1:9000/real-estate/new-image.jpg",
  "caption": "Beautiful living room view",
  "is_primary": false,
  "order_index": 1,
  "created_at": "2025-07-15T20:15:00Z"
}
```

### Update Property Image
**PUT** `/api/properties/{property_id}/images/{image_id}`

Update an existing property image.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `property_id` (int): The property ID
- `image_id` (int): The image ID

**Request Body:**
```json
{
  "caption": "Updated caption",
  "is_primary": true,
  "order_index": 0
}
```

**Response:** `200 OK`
```json
{
  "id": 24,
  "property_id": 15,
  "image_url": "http://127.0.0.1:9000/real-estate/new-image.jpg",
  "caption": "Updated caption",
  "is_primary": true,
  "order_index": 0,
  "created_at": "2025-07-15T20:15:00Z"
}
```

### Delete Property Image
**DELETE** `/api/properties/{property_id}/images/{image_id}`

Delete a property image.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `property_id` (int): The property ID
- `image_id` (int): The image ID

**Response:** `200 OK`
```json
{
  "message": "Image deleted successfully"
}
```

---

## Rental Applications

### Create Application
**POST** `/api/applications/`

Submit a rental application for a property.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "property_id": 1,
  "move_in_date": "2025-08-01T00:00:00Z",
  "lease_duration": 12,
  "monthly_income": 5000.0,
  "employment_status": "Full-time",
  "employer_name": "Tech Corp",
  "employer_contact": "hr@techcorp.com",
  "references": "[{\"name\": \"John Smith\", \"phone\": \"+1234567890\", \"relationship\": \"Previous landlord\"}]",
  "pets": "[{\"type\": \"dog\", \"breed\": \"Golden Retriever\", \"weight\": 65}]",
  "additional_notes": "I am a responsible tenant with excellent credit."
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "property_id": 1,
  "tenant_id": 1,
  "move_in_date": "2025-08-01T00:00:00Z",
  "lease_duration": 12,
  "monthly_income": 5000.0,
  "employment_status": "Full-time",
  "employer_name": "Tech Corp",
  "employer_contact": "hr@techcorp.com",
  "references": "[{\"name\": \"John Smith\", \"phone\": \"+1234567890\", \"relationship\": \"Previous landlord\"}]",
  "pets": "[{\"type\": \"dog\", \"breed\": \"Golden Retriever\", \"weight\": 65}]",
  "additional_notes": "I am a responsible tenant with excellent credit.",
  "status": "pending",
  "created_at": "2025-07-15T20:30:00Z",
  "updated_at": null
}
```

### Get User's Applications
**GET** `/api/applications/my-applications/`

Get all applications submitted by the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "property_id": 1,
    "tenant_id": 1,
    "move_in_date": "2025-08-01T00:00:00Z",
    "lease_duration": 12,
    "monthly_income": 5000.0,
    "employment_status": "Full-time",
    "employer_name": "Tech Corp",
    "employer_contact": "hr@techcorp.com",
    "references": "[{\"name\": \"John Smith\", \"phone\": \"+1234567890\", \"relationship\": \"Previous landlord\"}]",
    "pets": "[{\"type\": \"dog\", \"breed\": \"Golden Retriever\", \"weight\": 65}]",
    "additional_notes": "I am a responsible tenant with excellent credit.",
    "status": "pending",
    "created_at": "2025-07-15T20:30:00Z",
    "updated_at": null
  }
]
```

### Get Property Applications
**GET** `/api/applications/property/{property_id}`

Get all applications for a specific property. Must be the property owner.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `property_id` (int): The property ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "property_id": 1,
    "tenant_id": 1,
    "move_in_date": "2025-08-01T00:00:00Z",
    "lease_duration": 12,
    "monthly_income": 5000.0,
    "employment_status": "Full-time",
    "employer_name": "Tech Corp",
    "employer_contact": "hr@techcorp.com",
    "references": "[{\"name\": \"John Smith\", \"phone\": \"+1234567890\", \"relationship\": \"Previous landlord\"}]",
    "pets": "[{\"type\": \"dog\", \"breed\": \"Golden Retriever\", \"weight\": 65}]",
    "additional_notes": "I am a responsible tenant with excellent credit.",
    "status": "pending",
    "created_at": "2025-07-15T20:30:00Z",
    "updated_at": null
  }
]
```

### Update Application Status
**PUT** `/api/applications/{application_id}/status`

Update the status of a rental application. Must be the property owner.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `application_id` (int): The application ID

**Request Body:**
```json
{
  "status": "approved"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "property_id": 1,
  "tenant_id": 1,
  "status": "approved",
  "updated_at": "2025-07-15T21:00:00Z"
}
```

---

## Amenities

### Get All Amenities
**GET** `/api/properties/amenities/`

Get a list of all available amenities.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "WiFi",
    "description": "High-speed internet access",
    "icon": "wifi",
    "category": "utilities"
  },
  {
    "id": 2,
    "name": "Parking",
    "description": "Dedicated parking space",
    "icon": "car",
    "category": "utilities"
  }
]
```

---

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Status Codes
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Data Models

### User Roles
- `tenant`: Can browse properties and submit applications
- `landlord`: Can create and manage properties, review applications
- `admin`: Full system access

### Property Types
- `apartment`
- `house`
- `condo`
- `townhouse`
- `studio`

### Application Status
- `pending`: Application submitted, awaiting review
- `approved`: Application accepted
- `rejected`: Application declined
- `withdrawn`: Application withdrawn by applicant

---

## MinIO Integration

The API integrates with MinIO for image storage:

**MinIO Server:** `http://127.0.0.1:9000`  
**Bucket:** `real-estate` (publicly readable)  
**Web UI:** `http://127.0.0.1:53123`

### Public Image Access ✅
All property images are **publicly accessible** without authentication:

```html
<!-- Direct image access in HTML -->
<img src="http://127.0.0.1:9000/real-estate/30600318.png" alt="Property image" />
```

```javascript
// Direct fetch in JavaScript
fetch('http://127.0.0.1:9000/real-estate/image.jpg')
  .then(response => response.blob())
  .then(blob => {
    // Use the image blob
  });
```

### Image URLs
All property images are stored in MinIO and accessed via URLs like:
```
http://127.0.0.1:9000/real-estate/image-filename.jpg
```

**Example URLs from your current images:**
- `http://127.0.0.1:9000/real-estate/30600318.png`
- `http://127.0.0.1:9000/real-estate/32764679.jpeg`
- `http://127.0.0.1:9000/real-estate/34027421.jpeg`

### Supported Image Formats
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

### Frontend Integration
Your frontend can now:
1. **Display images directly** using the URLs returned from property endpoints
2. **No authentication required** for image access
3. **Use standard HTML img tags** or JavaScript fetch
4. **Implement image lazy loading** and caching

### Configuration Notes
- **Bucket Policy**: Configured for public read access (`s3:GetObject`)
- **Security**: Only GET requests are public; upload/delete still require authentication
- **CORS**: MinIO automatically handles CORS for image requests

---

## Getting Started

1. **Start the API server:**
   ```bash
   cd /Users/workingkakha/Documents/real-estate/back-end
   python app.py
   ```

2. **Start MinIO server:**
   ```bash
   minio server minio
   ```

3. **Access the documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

4. **Test the API:**
   - Register a new user
   - Login to get an access token
   - Create properties (as landlord)
   - Submit applications (as tenant)

---

## Support

For questions or issues, please refer to the API documentation at `/docs` or check the server logs for detailed error information.
