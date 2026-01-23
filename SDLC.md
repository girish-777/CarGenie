# CarGenie - Software Development Life Cycle (SDLC)

## What is SDLC?
**SDLC (Software Development Life Cycle)** is the process of building software step by step, from planning to deployment. Think of it like building a house - you need to plan, design, build, and maintain it.

---

## SDLC Phases for CarGenie

### Phase 1: Planning & Requirements
**What We Did:**
- **Understand the Goal**: Build an AI-powered car marketplace
- **Gather Requirements**: What features do users need?
  - User registration and login
  - Browse and search cars
  - View car details
  - Save favorites
  - Compare cars
  - Write reviews
  - AI recommendations
  - AI chatbot

**Deliverables:**
- Requirements document
- Feature list
- Technology choices

**Duration**: 1-2 weeks

---

### Phase 2: System Design
**What We Did:**
- **Architecture Design**: How will the system work?
  - Frontend (HTML/CSS/JavaScript)
  - Backend (FastAPI/Python)
  - Database (SQLite/PostgreSQL)
  - Vector Database (ChromaDB)
  - AI Services (OpenAI)

- **Database Design**: What tables do we need?
  - Users, Cars, Reviews, Favorites, Alerts

- **API Design**: What endpoints do we need?
  - `/api/v1/auth/*` - Authentication
  - `/api/v1/cars/*` - Car listings
  - `/api/v1/ai/*` - AI features

**Deliverables:**
- System design document
- Database schema
- API documentation
- Technology stack

**Duration**: 1-2 weeks

---

### Phase 3: Development (Implementation)
**What We Did:**
We built the website in multiple milestones/days:

#### Day 1: Project Setup
- Set up project structure
- Install dependencies
- Configure database
- Create basic FastAPI backend

#### Day 2: Authentication System
- User registration
- User login
- JWT token generation
- Password hashing

#### Day 3: Car Listings
- Database models (Car, CarSpec, CarScore)
- API endpoints for cars
- Frontend car listing page
- Basic search functionality

#### Day 4: Car Details & Features
- Car detail page
- Favorites functionality
- Frontend navigation

#### Day 5: Advanced Features
- Car comparison
- Reviews system
- User profile features

#### Day 6: AI Integration (Embeddings)
- Setup ChromaDB
- Generate car embeddings using OpenAI
- Store embeddings in vector database

#### Day 7: AI Features
- Similar cars recommendation
- Review summarization using AI
- Chatbot setup

#### Day 8: Global Chatbot
- Global floating chatbot widget
- Context-aware chatbot
- General car advice chatbot

**Deliverables:**
- Working code
- Features implemented
- Tested functionality

**Duration**: 8-10 days

---

### Phase 4: Testing
**What We Test:**
- **Unit Testing**: Test individual functions
  - Example: Test password hashing function
- **Integration Testing**: Test how components work together
  - Example: Test login → fetch cars → display
- **System Testing**: Test the entire system
  - Example: End-to-end user journey
- **User Acceptance Testing**: Real users test the website

**Test Scenarios:**
1. User can register and login ✅
2. User can browse cars ✅
3. User can search and filter cars ✅
4. User can view car details ✅
5. User can add favorites ✅
6. User can write reviews ✅
7. AI chatbot works ✅
8. Similar cars are recommended ✅

**Deliverables:**
- Test cases
- Bug reports
- Test results

**Duration**: 1-2 weeks

---

### Phase 5: Deployment
**What We Do:**
- **Environment Setup**:
  - Production server
  - Database setup (PostgreSQL)
  - Environment variables

- **Code Deployment**:
  - Deploy backend to cloud (AWS, Heroku, Railway)
  - Deploy frontend to static hosting (Netlify, Vercel)
  - Configure domain name

- **Database Migration**:
  - Migrate from SQLite to PostgreSQL
  - Run database migrations
  - Generate embeddings for all cars

**Deliverables:**
- Live website
- Production database
- Monitoring setup

**Duration**: 1 week

---

### Phase 6: Maintenance & Updates
**What We Do:**
- **Bug Fixes**: Fix issues reported by users
- **Feature Updates**: Add new features
- **Performance Optimization**: Make the website faster
- **Security Updates**: Keep the website secure
- **Content Updates**: Add new cars, update information

**Ongoing Tasks:**
- Monitor website performance
- User feedback collection
- Regular backups
- Security patches

**Duration**: Ongoing

---

## Simple SDLC Flow Diagram

```
┌─────────────────┐
│  1. Planning    │  ← What do we need to build?
│  & Requirements │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Design      │  ← How will we build it?
│  Architecture   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Development │  ← Building the code
│  (Coding)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. Testing     │  ← Does it work correctly?
│  Quality Check  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Deployment  │  ← Put it online for users
│  Go Live        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. Maintenance │  ← Keep it running & improve
│  & Updates      │
└─────────────────┘
```

---

## Development Methodology: Iterative Development

**What We Used:**
- **Iterative Approach**: Build features one at a time (Day 1, Day 2, etc.)
- **Agile-like**: Flexible, adapt to changes
- **Incremental**: Add features gradually

**Why This Approach:**
- ✅ Quick to see progress
- ✅ Easy to test each feature
- ✅ Can fix issues early
- ✅ Can adjust based on feedback

---

## Technology Stack Used

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling
- **JavaScript**: Interactivity

### Backend
- **FastAPI**: API framework
- **Python**: Programming language
- **SQLAlchemy**: Database ORM

### Database
- **SQLite**: Development database
- **PostgreSQL**: Production database (recommended)
- **ChromaDB**: Vector database for AI

### AI/ML
- **OpenAI API**: For embeddings and chatbot
- **text-embedding-3-small**: For car embeddings
- **gpt-3.5-turbo**: For chatbot and summarization

### Tools
- **Git**: Version control
- **Uvicorn**: Web server
- **Alembic**: Database migrations

---

## Timeline Summary

| Phase | Duration | Status |
|-------|----------|--------|
| 1. Planning & Requirements | 1-2 weeks | ✅ Complete |
| 2. System Design | 1-2 weeks | ✅ Complete |
| 3. Development | 8-10 days | ✅ Complete |
| 4. Testing | 1-2 weeks | 🔄 Ongoing |
| 5. Deployment | 1 week | 📅 Planned |
| 6. Maintenance | Ongoing | 📅 Continuous |

**Total Development Time**: ~4-6 weeks

---

## Key Milestones Completed

### ✅ Milestone 1: Basic Website (Day 1-3)
- User authentication
- Car listings
- Basic search

### ✅ Milestone 2: Core Features (Day 4-5)
- Car details
- Favorites
- Comparison
- Reviews

### ✅ Milestone 3: AI Features (Day 6-7)
- Vector embeddings
- Similar cars
- Review summarization

### ✅ Milestone 4: Enhanced AI (Day 8)
- Global chatbot
- Context-aware assistance

---

## Quality Assurance (QA) Process

### Code Quality
- **Code Reviews**: Check code before merging
- **Coding Standards**: Follow Python/JavaScript best practices
- **Documentation**: Code comments and documentation

### Testing Levels
1. **Development Testing**: Test during development
2. **Integration Testing**: Test features together
3. **User Testing**: Real users test the website
4. **Performance Testing**: Test speed and responsiveness

### Bug Tracking
- Identify bugs
- Prioritize fixes
- Track resolution
- Test fixes

---

## Risk Management

### Common Risks & Solutions

| Risk | Impact | Solution |
|------|--------|----------|
| API key exposure | High | Use environment variables |
| Database crashes | High | Regular backups |
| Slow performance | Medium | Optimize queries, use caching |
| Security breaches | High | HTTPS, input validation, password hashing |
| AI service downtime | Medium | Graceful error handling |

---

## Future Enhancements (Post-Launch)

### Phase 7: Additional Features
- **Mobile App**: iOS/Android applications
- **Advanced Search**: More filter options
- **Price Alerts**: Email notifications
- **Seller Portal**: Allow sellers to list cars
- **Payment Integration**: Online payment system
- **Admin Dashboard**: Manage cars and users

### Phase 8: Performance Optimization
- **Caching**: Redis for faster responses
- **CDN**: Faster image loading
- **Database Optimization**: Better queries
- **Load Balancing**: Handle more users

---

## Simple Explanation

**Think of SDLC like building a house:**

1. **Planning** → Decide what rooms you need (features)
2. **Design** → Draw blueprints (system design)
3. **Building** → Construct the house (coding)
4. **Inspection** → Check everything works (testing)
5. **Moving In** → Live in the house (deployment)
6. **Maintenance** → Fix things, add improvements (updates)

**For CarGenie:**
1. **Planning**: Decided to build a car marketplace with AI
2. **Design**: Designed frontend, backend, and database
3. **Development**: Coded all features day by day
4. **Testing**: Tested each feature as we built it
5. **Deployment**: Put it online for users (coming soon)
6. **Maintenance**: Keep improving based on feedback

---

## Development Team Roles

### Backend Developer
- Build API endpoints
- Database design
- AI integration
- Server setup

### Frontend Developer
- Build user interface
- User experience design
- Client-side logic
- Responsive design

### QA Tester
- Test features
- Report bugs
- Verify fixes
- User acceptance testing

### DevOps
- Server deployment
- Database management
- Monitoring
- Backup and recovery

---

## Success Criteria

### Functional Requirements ✅
- [x] Users can register and login
- [x] Users can browse cars
- [x] Users can search and filter
- [x] Users can view car details
- [x] Users can save favorites
- [x] Users can compare cars
- [x] Users can write reviews
- [x] AI features work correctly

### Non-Functional Requirements ✅
- [x] Website loads quickly
- [x] Secure authentication
- [x] Responsive design
- [x] Error handling
- [x] Code documentation

---

## Documentation Created

1. **Requirements Document**: What features are needed
2. **System Design Document**: How the system works
3. **Feature Design Document**: How each feature works
4. **API Documentation**: Available endpoints (auto-generated by FastAPI)
5. **SDLC Document**: This document - the development process

---

## Lessons Learned

### What Went Well ✅
- Iterative development allowed quick progress
- Modular architecture made features easy to add
- AI integration worked smoothly
- Clear separation of frontend/backend

### What Could Be Improved 🔄
- More automated testing
- Better error handling
- Performance optimization earlier
- More documentation during development

---

## Conclusion

The SDLC for CarGenie followed a simple, iterative approach:
1. Plan what to build
2. Design how to build it
3. Code the features
4. Test everything
5. Deploy online
6. Maintain and improve

This approach allowed us to:
- ✅ Build features quickly
- ✅ Test as we go
- ✅ Fix issues early
- ✅ Adapt to changes
- ✅ Deliver working software

**Current Status**: Development complete, ready for testing and deployment!

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Project**: CarGenie AI-Powered Automobile Website

