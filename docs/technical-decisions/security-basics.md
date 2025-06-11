# Security Basics for TRM-OS

This document outlines the fundamental security principles and practices that will be implemented in TRM-OS. The goal is to build a secure and trustworthy system from the ground up, protecting user data and ensuring the integrity of operations, aligning with the "integration-first mindset" and "robust error handling and security" emphasized in the project approach.

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính, biến và hàm trong ví dụ mã.

## Core Security Principles

1. **Defense in Depth**: Implement multiple layers of security controls. If one layer is breached, others are still in place.
2. **Principle of Least Privilege**: Users, agents, and services should only have the minimum necessary permissions to perform their tasks.
3. **Secure by Design**: Integrate security considerations into every phase of the development lifecycle, not as an afterthought.
4. **Secure by Default**: Configure systems and applications with secure settings by default.
5. **Data Minimization**: Collect and retain only the data that is strictly necessary for TRM-OS functionalities.
6. **Regular Audits and Updates**: Periodically review security configurations and keep all software components, libraries, and dependencies up-to-date with security patches.
7. **Fail Securely**: In case of failure, systems should default to a secure state (e.g., deny access rather than grant unintended access).

## 1. Authentication

- **Description**: Verifying the identity of users, agents, and services accessing TRM-OS.
- **Mechanisms**:
  - **User Authentication**:
    - For human users, TRM-OS will initially integrate with existing identity providers (e.g., Google Sign-In via OAuth 2.0) to leverage their robust security features.
    - Future considerations may include direct username/password authentication with strong password policies (complexity, rotation, MFA).
  - **Service/Agent Authentication**:
    - Internal services/agents will use token-based authentication (e.g., JSON Web Tokens - JWTs) for inter-service communication.
    - External API integrations will use OAuth 2.0 for services that support it, or API keys for others.
- **Key Considerations**:
  - **Strong Credentials**: Enforce strong password policies if direct authentication is implemented.
  - **Multi-Factor Authentication (MFA)**: Strongly recommended for all user accounts, especially administrative ones.
  - **Secure Token Handling**: Securely generate, store, transmit, and validate tokens. JWTs should be signed with strong algorithms (e.g., RS256/ES256) and have short expiry times.
  - **Session Management**: Implement secure session management practices (e.g., secure session IDs, timeouts, logout functionality).
- **Pseudo-code Example (JWT Generation - Conceptual)**:

  ```text
  FUNCTION generateUserJwt(userId, userRoles)
      payload = {
          "sub": userId, // Subject (user identifier)
          "roles": userRoles, // User roles for authorization
          "iss": "trm-os-auth-service", // Issuer
          "aud": "trm-os-api", // Audience
          "iat": CURRENT_TIMESTAMP(), // Issued at
          "exp": CURRENT_TIMESTAMP() + jwtExpiryDuration // Expiration time
      }
      // Sign the payload with a private key
      signedJwt = JWT_LIBRARY.sign(payload, authPrivateKey, ALGORITHM="RS256")
      RETURN signedJwt
  END FUNCTION

  FUNCTION verifyJwtAndGetUserContext(tokenString)
      TRY
          // Verify signature, expiration, issuer, audience
          decodedPayload = JWT_LIBRARY.verify(tokenString, authPublicKey, ALGORITHMS=["RS256"], AUDIENCE="trm-os-api")
          userContext = {
              "userId": decodedPayload.sub,
              "roles": decodedPayload.roles
          }
          RETURN userContext
      CATCH InvalidTokenError AS e
          LOG_WARNING("Invalid JWT received", e)
          RETURN NULL // Or throw an authentication exception
      END TRY
  END FUNCTION
  ```

## 2. Authorization

- **Description**: Determining what an authenticated user, agent, or service is allowed to do within TRM-OS.
- **Mechanisms**:
  - **Role-Based Access Control (RBAC)**: Define roles (e.g., `Founder`, `TeamMember`, `AdminAgent`, `IntegrationAgent`) with specific sets of permissions. Users and agents are assigned roles.
  - **Attribute-Based Access Control (ABAC)**: (Future consideration) Permissions can also be based on attributes of the user, resource, or environment (e.g., a user can only access projects they own or are assigned to).
- **Key Considerations**:
  - **Granular Permissions**: Define permissions at a fine-grained level (e.g., `read_task`, `create_project`, `manage_integration_X`).
  - **Centralized Policy Enforcement**: Authorization checks should be performed consistently at API endpoints and service boundaries.
  - **Regular Review**: Periodically review roles and permissions to ensure they are still appropriate.
- **Pseudo-code Example (API Endpoint Authorization Check)**:

  ```text
  FUNCTION handleApiRequestGetProject(request, projectId)
      // 1. Authenticate user (e.g., via JWT middleware, sets userContext on request)
      userContext = request.userContext
      IF userContext IS NULL THEN
          RETURN HTTP_401_UNAUTHORIZED
      END IF

      // 2. Perform authorization check
      // Example: User must have 'readProject' permission AND
      // (be an admin OR be the owner of the project OR be a member of the project)
      hasPermission = CHECK_PERMISSION(userContext.roles, "readProject")
      IF NOT hasPermission THEN
          RETURN HTTP_403_FORBIDDEN
      END IF

      project = CALL database.getProjectDetails(projectId)
      IF project IS NULL THEN
          RETURN HTTP_404_NOT_FOUND
      END IF

      isAdmin = "admin" IN userContext.roles
      isOwner = project.ownerId == userContext.userId
      isMember = IS_PROJECT_MEMBER(userContext.userId, projectId)

      IF NOT (isAdmin OR isOwner OR isMember) THEN
          RETURN HTTP_403_FORBIDDEN
      END IF

      // 3. Proceed with request handling
      RETURN HTTP_200_OK (projectData = project)
  END FUNCTION
  ```

## 3. Data Security

- **Description**: Protecting data at rest, in transit, and during processing.
- **Mechanisms**:
  - **Encryption in Transit**: Use HTTPS/TLS for all external and internal API communications.
  - **Encryption at Rest**:
    - Encrypt sensitive data stored in databases (e.g., Supabase, Neo4j Aura often provide this by default or as a configurable option).
    - Encrypt backups.
  - **Secrets Management**:
    - Use a dedicated secrets management solution (e.g., HashiCorp Vault, cloud provider's secrets manager) or secure environment variables for API keys, database credentials, and other secrets.
    - **DO NOT hardcode secrets in code or configuration files.**
  - **Data Masking/Anonymization**: For non-production environments or analytics, consider masking or anonymizing sensitive data.
- **Key Considerations**:
  - **Strong Encryption Algorithms**: Use industry-standard, strong encryption algorithms and appropriate key lengths.
  - **Key Management**: Securely manage encryption keys.
  - **Input Validation**: Validate and sanitize all user/external inputs to prevent injection attacks (SQL injection, XSS, etc.).
  - **Output Encoding**: Encode data correctly when displaying it in user interfaces or including it in different contexts to prevent XSS.
- **Pseudo-code Example (Securely Fetching an API Key for an Integration)**:

  ```text
  FUNCTION getApiKeyForService(serviceName, userId) // userId for user-specific keys
      // Construct the secret identifier, e.g., "trmos_user_{userId}_service_{serviceName}_apikey"
      secretPathOrEnvVarName = FORMAT_SECRET_IDENTIFIER(userId, serviceName)

      // Attempt to retrieve from a secrets manager first
      TRY
          apiKey = CALL secrets_manager_client.getSecret(secretPathOrEnvVarName)
          IF apiKey IS NOT NULL THEN
              RETURN apiKey
          END IF
      CATCH SecretsManagerError AS e
          LOG_WARNING("Failed to retrieve secret from manager for " + serviceName, e)
      END TRY

      // Fallback to environment variable (less ideal for per-user keys but ok for system-wide keys)
      apiKey = GET_ENVIRONMENT_VARIABLE(secretPathOrEnvVarName)
      IF apiKey IS NOT NULL THEN
          RETURN apiKey
      END IF

      LOG_ERROR("API key for service " + serviceName + " not found for user " + userId)
      RETURN NULL
  END FUNCTION
  ```

## 4. API Security

- **Description**: Securing TRM-OS APIs (both internal and external-facing).
- **Mechanisms**:
  - **Authentication & Authorization**: As described above, all API endpoints must enforce authentication and authorization.
  - **Input Validation**: Rigorously validate all incoming API request parameters and payloads against defined schemas (e.g., using Pydantic models).
  - **Rate Limiting**: Implement rate limiting to protect against DoS attacks and abuse.
  - **HTTPS Only**: All API endpoints must be served over HTTPS.
  - **Secure Headers**: Use security-related HTTP headers (e.g., `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`).
  - **Logging and Monitoring**: Log all API requests and responses (excluding sensitive data) for auditing and threat detection.
- **Key Considerations**:
  - **Clear API Contracts**: Use OpenAPI/Swagger to define and document API contracts.
  - **Error Handling**: Return standardized, non-revealing error messages. Avoid leaking internal system details in error responses.

## 5. Operational Security

- **Description**: Security practices related to the deployment, maintenance, and monitoring of TRM-OS.
- **Mechanisms**:
  - **Secure Deployment**:
    - Automate deployment processes (CI/CD) to reduce manual errors.
    - Scan dependencies for known vulnerabilities.
  - **Logging and Monitoring**:
    - Implement centralized logging for all system components.
    - Monitor logs for suspicious activities and security events.
    - Set up alerts for critical security events.
  - **Patch Management**: Regularly update operating systems, application frameworks, and all third-party libraries.
  - **Backup and Recovery**: Implement regular, automated, and tested backup and recovery procedures. Securely store backups.
  - **Incident Response Plan**: Develop a plan to respond to security incidents, including steps for containment, eradication, recovery, and post-incident analysis.
- **Key Considerations**:
  - **Secure Access to Infrastructure**: Limit access to production infrastructure and use strong authentication (e.g., SSH keys, MFA).
  - **Vulnerability Scanning**: Regularly scan applications and infrastructure for vulnerabilities.

## 6. Compliance

- **Description**: Adhering to relevant data privacy and security regulations (e.g., GDPR, CCPA, depending on user base and data processed).
- **Key Considerations**:
  - **Data Subject Rights**: Implement mechanisms to support data subject rights (e.g., access, rectification, erasure).
  - **Privacy by Design**: Integrate privacy considerations into system design.
  - **Data Processing Agreements**: Ensure appropriate agreements are in place with any third-party data processors.

This document provides a foundational overview. Specific implementation details will be elaborated upon during the development of each component and feature. Security is an ongoing process, not a one-time task.
