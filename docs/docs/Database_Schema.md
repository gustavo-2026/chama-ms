# ChamaVault Database Schema

## Organizations (Tenants)

```prisma
model Organization {
  id              String   @id @default(cuid())
  name            String
  slug            String   @unique // for white-label: mychama.chamavault.com
  phone           String
  email           String?
  logoUrl         String?
  primaryColor    String   @default("#7C3AED") // violet default
  shortcode       String?  // M-Pesa business shortcode
  mpesaEnv       String   @default("sandbox") // sandbox | production
  
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  members         OrganizationMember[]
  contributions   Contribution[]
  loans           Loan[]
  transactions    Transaction[]
  proposals       Proposal[]
}
```

## Members

```prisma
model Member {
  id              String   @id @default(cuid())
  organizationId  String
  userId          String?  // link to User if has app account
  phone           String   @unique
  name            String
  role            MemberRole @default(MEMBER)
  contributionTier String  @default("regular") // regular, silver, gold
  mpesaLinked     Boolean  @default(false)
  mpesaPhone      String?  // verified M-Pesa number
  
  organization    Organization @relation(fields: [organizationId], references: [id])
  
  contributions   Contribution[]
  loans           Loan[]
  
  createdAt       DateTime @default(now())
}

enum MemberRole {
  MEMBER
  TREASURER
  CHAIR
  AGENT
}
```

## Contributions

```prisma
model Contribution {
  id              String   @id @default(cuid())
  organizationId  String
  memberId        String
  amount          Decimal  @db.Decimal(12, 2)
  method          ContributionMethod // CASH, MPESA, BANK
  status          TransactionStatus @default(PENDING)
  mpesaReceipt    String?
  periodMonth      //      Int1-12
  periodYear      Int
  
  member          Member   @relation(fields: [memberId], references: [id])
  organization    Organization @relation(fields: [organizationId], references: [id])
  
  createdAt       DateTime @default(now())
}

enum ContributionMethod {
  CASH
  MPESA
  BANK
}
```

## Loans

```prisma
model Loan {
  id              String   @id @default(cuid())
  organizationId  String
  memberId        String
  amount          Decimal  @db.Decimal(12, 2)
  interestRate    Decimal  @db.Decimal(5, 2) // e.g., 10.00 = 10%
  status          LoanStatus @default(PENDING)
  purpose         String?
  
  repayments      LoanRepayment[]
  
  member          Member   @relation(fields: [memberId], references: [id])
  organization    Organization @relation(fields: [organizationId], references: [id])
  
  createdAt       DateTime @default(now())
  approvedAt      DateTime?
  dueDate         DateTime?
}

enum LoanStatus {
  PENDING
  APPROVED
  REJECTED
  ACTIVE
  PAID
}

model LoanRepayment {
  id              String   @id @default(cuid())
  loanId          String
  amount          Decimal  @db.Decimal(12, 2)
  method          ContributionMethod
  status          TransactionStatus @default(PENDING)
  
  loan            Loan     @relation(fields: [loanId], references: [id])
  
  createdAt       DateTime @default(now())
}
```

## M-Pesa Transactions

```prisma
model Transaction {
  id              String   @id @default(cuid())
  organizationId  String
  memberId        String?
  
  type            MpesaType // C2B, B2C, STK_IN, STK_OUT
  amount          Decimal  @db.Decimal(12, 2)
  status          TransactionStatus @default(PENDING)
  
  mpesaReceipt    String?  // M-Pesa receipt number
  mpesaConversation String?
  mpesaOriginator String?
  
  phone           String?
  note            String?
  
  organization    Organization @relation(fields: [organizationId], references: [id])
  
  createdAt       DateTime @default(now())
  processedAt     DateTime?
}

enum MpesaType {
  C2B     // Member paying chama
  B2C     // Chama paying member
  STK_IN  // STK push received
  STK_OUT // STK push sent
}

enum TransactionStatus {
  PENDING
  COMPLETED
  FAILED
  CANCELLED
}
```

## Governance

```prisma
model Proposal {
  id              String   @id @default(cuid())
  organizationId  String
  title           String
  description     String
  type            ProposalType
  status          ProposalStatus @default(DRAFT)
  
  votes           Vote[]
  
  organization    Organization @relation(fields: [organizationId], references: [id])
  
  createdAt       DateTime @default(now())
  votingStarts    DateTime?
  votingEnds      DateTime?
}

enum ProposalType {
  CONTRIBUTION_CHANGE
  LOAN_POLICY
  DIVIDEND
  EXPULSION
  CONSTITUTION_AMENDMENT
  OTHER
}

enum ProposalStatus {
  DRAFT
  PUBLISHED
  VOTING
  PASSED
  REJECTED
}

model Vote {
  id              String   @id @default(cuid())
  proposalId      String
  memberId        String
  choice          VoteChoice
  
  proposal        Proposal @relation(fields: [proposalId], references: [id])
  member          Member   @relation(fields: [memberId], references: [id])
  
  createdAt       DateTime @default(now())
}

enum VoteChoice {
  YES
  NO
  ABSTAIN
}
```

## Notifications

```prisma
model Notification {
  id              String   @id @default(cuid())
  organizationId  String
  memberId        String?
  
  type            NotificationType
  title           String
  message         String
  channel         Channel // IN_APP, SMS, EMAIL
  status          String  @default("SENT") // SENT, DELIVERED, FAILED
  
  sentAt          DateTime @default(now())
}

enum NotificationType {
  CONTRIBUTION_REMINDER
  LOAN_APPROVED
  LOAN_REJECTED
  LOAN_DUE_SOON
  LOAN_OVERDUE
  DIVIDEND_DISBURSED
  VOTE_STARTED
  VOTE_ENDED
}
```

---

## Key Design Decisions

1. **Phone as primary identifier** — Kenyan market, M-Pesa native
2. **Organization = Chama** — each chama is a tenant
3. **Decimal for money** — never use floats for currency
4. **Soft deletes** — preserve history for audit
5. **Timestamps everywhere** — createdAt, updatedAt on all models
