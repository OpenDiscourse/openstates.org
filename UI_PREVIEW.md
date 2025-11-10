# Analysis Dashboard UI Preview

This document describes the user interface of the Analysis Dashboard.

## Page Layouts

### 1. Dashboard Home (`/analysis/`)

```
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Dashboard                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   1,234  │  │    567   │  │     5    │  │     2    │  │
│  │ Analyses │  │ Profiles │  │ Pending  │  │ Running  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Tools                                                 │  │
│  │ [Data Explorer] [Search Legislators] [Run Analysis]  │  │
│  │ [View Jobs] [Ingestion Logs]                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Recent Analysis Jobs                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ID │ Type        │ Status   │ Created    │ Progress  │  │
│  │ 12 │ NLP         │ Running  │ Nov 10 10am│ 45%      │  │
│  │ 11 │ Embeddings  │ Complete │ Nov 10 9am │ 100%     │  │
│  │ 10 │ Sentiment   │ Complete │ Nov 10 8am │ 100%     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Recent Data Ingestions                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ID │ Database        │ Status   │ Stats              │  │
│  │ 5  │ localhost/db    │ Complete │ 5234 bills, 12456  │  │
│  │ 4  │ cloudcurio.cc   │ Complete │ 3421 bills, 8234   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Four statistics cards with live updates
- Quick access buttons to all tools
- Recent jobs table with status badges
- Recent ingestions table with stats

### 2. Data Explorer (`/analysis/explorer/`)

```
┌─────────────────────────────────────────────────────────────┐
│                      Data Explorer                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Select Jurisdiction:  [Texas ▼]                      │  │
│  │ Select Session:       [2023 ▼]                       │  │
│  │                       [Explore]                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Data Summary                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  5,234   │  │ 12,456   │  │   181    │  │    50    │  │
│  │  Bills   │  │  Votes   │  │  People  │  │   Orgs   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  Available Actions                                          │
│  [Download Bulk Data] [Run Analysis] [GraphQL API]         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Jurisdiction dropdown
- Session filter
- Live data counts
- Quick action buttons

### 3. Legislator Search (`/analysis/legislators/search/`)

```
┌─────────────────────────────────────────────────────────────┐
│                   Search Legislators                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Search by Name: [John Smith____________]             │  │
│  │ Jurisdiction:   [Texas ▼]                            │  │
│  │                 [Search]                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Results (25)                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Name          │ Party      │ Jurisdiction  │ Action  │  │
│  │ John Smith    │ Democrat   │ Texas         │ [View]  │  │
│  │ Jane Smith    │ Republican │ Texas         │ [View]  │  │
│  │ Bob Johnson   │ Democrat   │ California    │ [View]  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Name search field
- Jurisdiction filter
- Results table
- Quick view buttons

### 4. Legislator Profile (`/analysis/legislator/<id>/`)

```
┌─────────────────────────────────────────────────────────────┐
│                    John Smith                                │
│                    [Photo]                                   │
│                    Democrat • State Representative           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Voting Record                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  1,234   │  │   856    │  │   298    │  │    80    │  │
│  │  Total   │  │   Yes    │  │    No    │  │ Abstain  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  Sponsored Legislation                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │   234    │  │   156    │  │    78    │                 │
│  │  Total   │  │ Primary  │  │Co-Sponsor│                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                              │
│  Primary Topics                                             │
│  [Healthcare] [Education] [Budget] [Environment]            │
│                                                              │
│  Recent Votes (Last 20)                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Date   │ Bill    │ Motion           │ Vote           │  │
│  │ Nov 10 │ HB 123  │ Final passage    │ [Yes]          │  │
│  │ Nov 9  │ HB 124  │ Committee report │ [Yes]          │  │
│  │ Nov 8  │ SB 456  │ Amendment        │ [No]           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Sponsored Bills (Last 20)                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Session│ Bill   │ Title            │ Role  │Analysis │  │
│  │ 2023   │ HB 123 │ Education funding│Primary│[✓]      │  │
│  │ 2023   │ HB 124 │ Healthcare reform│Co-spon│        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [Back to Search] [Dashboard]                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Profile header with photo
- Voting statistics (4 cards)
- Sponsorship statistics (3 cards)
- Topic badges
- Recent votes table
- Sponsored bills table
- Analysis status indicators

### 5. Jobs List (`/analysis/jobs/`)

```
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Jobs                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Filter by Type:   [NLP ▼]                            │  │
│  │ Filter by Status: [Running ▼]                        │  │
│  │                   [Apply Filters]                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ID│Type      │Status  │Created  │Updated  │Progress │  │
│  │ 12│NLP       │Running │Nov 10   │Nov 10   │▓▓▓▓░░░░ │  │
│  │   │          │        │10:00    │10:15    │455/1000 │  │
│  │ 11│Embeddings│Complete│Nov 10   │Nov 10   │▓▓▓▓▓▓▓▓ │  │
│  │   │          │        │09:00    │09:30    │1000/1000│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [Create New Job] [Back to Dashboard]                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Type and status filters
- Jobs table with progress bars
- Real-time status updates
- Links to job details

### 6. Run Analysis (`/analysis/run-analysis/`)

```
┌─────────────────────────────────────────────────────────────┐
│                   Run Analysis Job                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Analysis Type:    [NLP Analysis ▼]                   │  │
│  │ Jurisdiction:     [Texas ▼]                          │  │
│  │ Session:          [2023 ▼]                           │  │
│  │                                                       │  │
│  │ [Submit Job] [Cancel]                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Available Analysis Types                                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ NLP Analysis                                          │  │
│  │ Extract topics, entities, and sentiment from bill    │  │
│  │ text using natural language processing.              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Embeddings Generation                                 │  │
│  │ Generate vector embeddings for bills using sentence  │  │
│  │ transformers for similarity search.                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Analysis type dropdown
- Optional filters
- Submit button
- Description cards for each type

### 7. Ingestion Logs (`/analysis/ingestion-logs/`)

```
┌─────────────────────────────────────────────────────────────┐
│                Bulk Data Ingestion Logs                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ID│Database           │Jurisdic│Status  │Statistics  │  │
│  │5 │localhost/openstates│tx,ca,ny│Complete│Bills: 5234 │  │
│  │  │                    │        │        │Votes: 12456│  │
│  │4 │cloudcurio.cc/db    │tx      │Complete│Bills: 3421 │  │
│  │  │                    │        │        │Votes: 8234 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  CLI Command                                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ To perform bulk data ingestion, use:                  │  │
│  │                                                       │  │
│  │ python manage.py bulk_ingest \                       │  │
│  │   --connection-string "postgresql://..." \           │  │
│  │   --jurisdictions "tx,ca,ny"                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Ingestion history table
- Connection details (no credentials)
- Statistics summary
- CLI command examples

## UI Components

### Status Badges

```
[Pending]   - Yellow/Orange background
[Running]   - Blue background
[Complete]  - Green background
[Failed]    - Red background
```

### Progress Bars

```
▓▓▓▓░░░░ 45%    (45% complete)
▓▓▓▓▓▓▓▓ 100%   (100% complete)
```

### Statistics Cards

```
┌──────────┐
│  1,234   │  ← Large number
│  Label   │  ← Description
└──────────┘
```

### Topic Badges

```
[Healthcare] [Education] [Budget]
```

### Vote Badges

```
[Yes]     - Green
[No]      - Red
[Abstain] - Gray
[Other]   - Gray
```

## Color Scheme

Based on Foundation CSS framework:

- **Primary**: `#1779ba` (Blue) - Buttons, links, accents
- **Success**: `#3adb76` (Green) - Completed status, yes votes
- **Warning**: `#ffae00` (Orange) - Pending status
- **Alert**: `#cc4b37` (Red) - Failed status, no votes
- **Gray**: `#f4f4f4` - Backgrounds, disabled states

## Typography

- **Headings**: Sans-serif, bold
- **Body**: Sans-serif, regular
- **Code**: Monospace font
- **Sizes**:
  - h1: 2.5rem
  - h2: 2rem
  - h3: 1.5rem
  - Body: 1rem
  - Small: 0.875rem

## Responsive Design

All pages are responsive and work on:
- Desktop (1920px+)
- Laptop (1366px+)
- Tablet (768px+)
- Mobile (320px+)

Foundation's grid system ensures proper layout on all devices.

## Accessibility

- Semantic HTML5 elements
- ARIA labels where appropriate
- Keyboard navigation support
- Color contrast ratios meet WCAG standards
- Screen reader friendly

## Interactive Elements

### Real-time Updates

- Statistics cards refresh every 10 seconds
- Job progress updates every 10 seconds
- Status badges update dynamically

### Form Validation

- Required fields marked
- Input validation
- Error messages displayed inline
- Success feedback on submission

### Loading States

- Buttons show loading spinner when clicked
- Tables show "Loading..." message
- Progress bars animate smoothly

## Navigation

All pages include:
- Header with site navigation
- Footer with links
- Back buttons to previous pages
- Dashboard link always accessible

## Integration with Existing UI

The Analysis Dashboard seamlessly integrates with the existing OpenStates UI:
- Uses Foundation CSS (same as existing pages)
- Matches existing color scheme
- Consistent header/footer
- Similar navigation patterns
- Same typography and spacing

This ensures a cohesive user experience across the entire platform.
