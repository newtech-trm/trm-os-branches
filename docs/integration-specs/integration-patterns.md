# Integration Patterns for TRM-OS

This document outlines the common patterns for integrating TRM-OS with external tools and services. These patterns will guide the development of specific connectors and ensure consistency and reliability in data exchange. The primary goal is to enable TRM-OS to seamlessly connect with the existing TRM ecosystem (e.g., Gmail, Google Sheets, CRM) as described in the overall TRM-OS vision.

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính, trạng thái và sự kiện.

## 1. Webhook Receivers

- **Description**: TRM-OS will expose secure HTTP(S) endpoints to receive real-time event notifications (webhooks) from external systems. This is the preferred method for services that support sending outbound webhooks upon data changes or specific events. This allows TRM-OS to react promptly to external stimuli, a core aspect of the "Recognition → Event → WIN" philosophy.

- **Use Cases**:
    - Receiving notifications from project management tools (e.g., new task created, task status updated, project completion).
    - Getting alerts from communication platforms (e.g., new important email in Gmail via Google Cloud Pub/Sub, new message in a specific Slack channel that might indicate a `Tension` or `Recognition`).
    - Updates from CRM systems (e.g., new contact added, deal stage changed, new customer interaction logged).

- **Key Considerations**:
    - **Security**: Endpoints must be secured (e.g., using HTTPS, request signature verification, API keys/shared secrets).
    - **Payload Handling**: Robust parsing and validation of incoming webhook payloads against expected schemas.
    - **Idempotency**: Design handlers to be idempotent to gracefully handle duplicate webhook deliveries from external systems.
    - **Asynchronous Processing**: Offload potentially long-running processing (e.g., complex data transformation, AI analysis) to background tasks/queues to respond quickly to the webhook source (e.g., with a `202 Accepted`) and avoid timeouts.
    - **Error Handling & Logging**: Comprehensive logging of incoming webhooks (headers, payload snippets for debugging), processing status, and any errors encountered. Implement dead-letter queues or retry mechanisms for failed processing.
    - **Transformation**: Map incoming webhook data to TRM-OS internal `Event` entities and other relevant ontology objects (e.g., a new email might trigger a `PotentialTensionDetectedEvent`).
    - **Scalability**: Ensure webhook endpoints can handle bursts of traffic.

- **Pseudo-code Example**:

```text
FUNCTION handle_external_webhook(request_headers, request_payload, source_system_name)
    // 1. Authenticate/Authorize the request
    // Example: Verify a signature or API key specific to source_system_name
    IF NOT is_valid_source(request_headers, source_system_name) THEN
        LOG_ERROR("Unauthorized webhook attempt from: " + source_system_name)
        RETURN HTTP_401_UNAUTHORIZED
    END IF

    // 2. Basic payload validation (e.g., presence of essential fields)
    IF NOT is_valid_payload_structure(request_payload) THEN
        LOG_ERROR("Invalid payload structure from: " + source_system_name, request_payload)
        RETURN HTTP_400_BAD_REQUEST
    END IF

    // 3. Generate a unique ID for this event
    event_id = GENERATE_UUID()
    LOG_INFO("Webhook received from: " + source_system_name + ", Event ID: " + event_id)

    // 4. Enqueue for asynchronous processing
    // The message should include payload, source_system_name, event_id, and any relevant metadata
    TRY
        CALL message_queue.publish(
            queue_name = "external_events_processing_queue",
            message_body = {
                "event_id": event_id,
                "source_system": source_system_name,
                "received_at": CURRENT_TIMESTAMP(),
                "payload": request_payload
            }
        )
        LOG_INFO("Event ID: " + event_id + " enqueued for processing.")
        // 5. Respond immediately to acknowledge receipt
        RETURN HTTP_202_ACCEPTED
    CATCH MessageQueueError AS e
        LOG_CRITICAL("Failed to enqueue webhook event ID: " + event_id, e)
        // Potentially save to a fallback store or trigger an alert
        RETURN HTTP_500_INTERNAL_SERVER_ERROR
    END TRY
END FUNCTION

// Separate worker/consumer for the message queue
FUNCTION process_queued_webhook_event(queued_message)
    LOG_INFO("Processing event ID: " + queued_message.event_id + " from: " + queued_message.source_system)
    // 1. Detailed parsing and validation of the payload (e.g., using Pydantic models)
    parsed_data = PARSE_AND_VALIDATE_PAYLOAD(queued_message.payload, queued_message.source_system)
    IF parsed_data IS NULL THEN
        LOG_ERROR("Failed to parse/validate payload for event ID: " + queued_message.event_id)
        // Move to dead-letter queue or log for manual review
        RETURN
    END IF

    // 2. Transform parsed_data into TRM-OS Event(s) and other entities
    trm_os_events = TRANSFORM_TO_TRM_OS_EVENTS(parsed_data, queued_message.source_system)

    // 3. Persist TRM-OS Event(s) and related entities to database (e.g., Neo4j)
    FOREACH event IN trm_os_events
        CALL database.save_event(event)
        // Potentially trigger further actions based on the event type
        CALL trigger_internal_workflows(event)
    END FOREACH
    LOG_INFO("Successfully processed event ID: " + queued_message.event_id)
END FUNCTION
```

## 2. Polling Agents

- **Description**: For external systems that do not support webhooks or where real-time updates are not critical (or feasible due to API limitations), TRM-OS will use polling agents. These agents will periodically query the external system's API to fetch new or updated data.

- **Use Cases**:
    - Regularly syncing data from Google Sheets (e.g., project lists, task statuses, resource allocations).
    - Fetching updates from legacy systems or APIs with limited eventing capabilities.
    - Checking for new files in cloud storage (e.g., Google Drive) that might contain `KnowledgeSnippet`s or project-related documents.

- **Key Considerations**:
    - **Frequency**: Configurable polling intervals per integration, balancing data freshness with API rate limits and system load.
    - **State Management**: Persistently store the last polled state (e.g., last updated timestamp, last processed ID, ETag) for each integration to avoid redundant data fetching and processing.
    - **API Rate Limiting**: Strictly respect the rate limits of external APIs. Implement intelligent backoff strategies (e.g., exponential backoff) upon encountering rate limit errors or other transient API failures.
    - **Efficiency**: Fetch only changed or new data whenever possible (e.g., using delta queries, filtering by modification date, using conditional GET requests with ETags).
    - **Error Handling**: Robust handling of API errors, network issues, and unexpected data formats. Implement retry mechanisms for transient errors.
    - **Transformation**: Map fetched data to TRM-OS entities, including logic to identify new vs. updated items.

- **Pseudo-code Example**:

```text
FUNCTION run_polling_agent(integration_config)
    LOG_INFO("Starting polling agent for: " + integration_config.source_system_name)

    // 1. Retrieve last polled state (e.g., last_processed_timestamp)
    last_state = CALL database.get_polling_state(integration_config.source_system_name)
    IF last_state IS NULL THEN
        last_state = INITIAL_POLLING_STATE() // e.g., a very old timestamp or beginning of epoch
    END IF

    // 2. Construct API request based on last_state
    // Example: fetch items modified after last_processed_timestamp
    api_request_parameters = { "modified_since": last_state.last_processed_timestamp }

    TRY
        // 3. Call external API
        api_client = GET_API_CLIENT(integration_config) // Handles auth
        raw_data_items = CALL api_client.fetch_data(api_request_parameters)
    CATCH APIError AS e
        LOG_ERROR("API error polling " + integration_config.source_system_name, e)
        // Implement backoff or alert
        RETURN
    END TRY

    IF IS_EMPTY(raw_data_items) THEN
        LOG_INFO("No new data from: " + integration_config.source_system_name)
        CALL database.update_polling_state(integration_config.source_system_name, last_state.last_processed_timestamp) // Update "last checked" time
        RETURN
    END IF

    new_max_timestamp = last_state.last_processed_timestamp
    processed_item_count = 0

    // 4. Process fetched items
    FOREACH item IN raw_data_items
        // 5. Transform raw_data_item into TRM-OS entities/events
        trm_os_entity = TRANSFORM_RAW_ITEM(item, integration_config.source_system_name)
        IF trm_os_entity IS NULL THEN
            LOG_WARNING("Failed to transform item: ", item)
            CONTINUE
        END IF

        // 6. Save to TRM-OS database (handle create vs. update logic)
        CALL database.save_or_update_entity(trm_os_entity)
        processed_item_count = processed_item_count + 1

        // 7. Update new_max_timestamp if applicable
        IF item.timestamp > new_max_timestamp THEN
            new_max_timestamp = item.timestamp
        END IF
    END FOREACH

    // 8. Update polling state with the new_max_timestamp (or other cursor)
    CALL database.update_polling_state(integration_config.source_system_name, new_max_timestamp)
    LOG_INFO("Polling agent for " + integration_config.source_system_name + " completed. Processed " + processed_item_count + " items.")
END FUNCTION
```

## 3. OAuth 2.0 / API Key Authentication

- **Description**: For accessing user-specific data or services requiring authenticated access, TRM-OS will implement standard and secure authentication mechanisms.
    - **OAuth 2.0**: This is the preferred method for services like Google Workspace (Gmail, Drive, Sheets, Calendar), Microsoft Graph, and other modern SaaS platforms. TRM-OS will guide users through the standard OAuth 2.0 authorization code grant flow and securely store access tokens and refresh tokens.
    - **API Keys/Tokens**: For services that use static API keys, personal access tokens, or other token-based authentication. These will be securely stored and managed within TRM-OS.

- **Use Cases**:
    - Accessing a Founder's Gmail inbox to detect `Tension`s or `Recognition`s from email content.
    - Reading/writing data to a user's Google Sheets for project tracking or data input.
    - Interacting with CRM APIs on behalf of the user to log activities or retrieve customer data.

- **Key Considerations**:
    - **Secure Token/Key Storage**: Encrypt and securely store all OAuth tokens (access and refresh) and API keys (e.g., using a dedicated secrets management solution or encrypted database fields).
    - **Token Refresh**: Implement robust logic to automatically refresh OAuth access tokens using refresh tokens before they expire.
    - **Scope Management**: Request only the minimum necessary permissions (scopes) during the OAuth flow to adhere to the principle of least privilege.
    - **Error Handling**: Gracefully handle token expiration, revocation, invalid credentials, and other authentication/authorization failures. Provide clear guidance to the user if re-authentication is needed.
    - **User Experience**: Provide a clear, secure, and user-friendly process for users to authorize TRM-OS to access their external accounts. Clearly explain what permissions are being requested and why.
    - **Revocation**: Allow users to easily revoke TRM-OS's access to their external accounts.

- **Pseudo-code Example (OAuth 2.0 Token Refresh and API Call)**:

```text
FUNCTION get_google_api_client(user_id)
    // 1. Retrieve stored OAuth tokens for the user
    tokens = CALL database.get_oauth_tokens(user_id, "google")
    IF tokens IS NULL THEN
        THROW AuthenticationRequiredException("User has not authorized Google access.")
    END IF

    access_token = tokens.access_token
    refresh_token = tokens.refresh_token
    expires_at = tokens.expires_at

    // 2. Check if access token is expired or close to expiring
    IF CURRENT_TIMESTAMP() >= expires_at - BUFFER_TIME THEN
        LOG_INFO("Access token for user " + user_id + " expired or nearing expiry. Refreshing...")
        TRY
            new_tokens = CALL google_oauth_service.refresh_access_token(refresh_token)
            // 3. Store new tokens (new access token, potentially new refresh token, new expiry)
            CALL database.update_oauth_tokens(user_id, "google", new_tokens)
            access_token = new_tokens.access_token
            LOG_INFO("Access token refreshed successfully for user " + user_id)
        CATCH TokenRefreshError AS e
            LOG_ERROR("Failed to refresh access token for user " + user_id, e)
            // Mark integration as needing re-authentication
            CALL database.set_integration_status(user_id, "google", "reauthRequired")
            THROW AuthenticationFailedException("Token refresh failed.")
        END TRY
    END IF

    // 4. Initialize API client with valid access token
    api_client = INITIALIZE_GOOGLE_API_CLIENT(access_token)
    RETURN api_client
END FUNCTION

FUNCTION read_user_emails(user_id)
    TRY
        google_client = CALL get_google_api_client(user_id)
        emails = CALL google_client.gmail_service.list_messages(query="is:unread label:inbox")
        RETURN emails
    CATCH AuthenticationRequiredException AS e
        // Prompt user to re-authenticate
        NOTIFY_USER_REAUTH_NEEDED(user_id, "google")
        RETURN EMPTY_LIST
    CATCH AuthenticationFailedException AS e
        // Log error, potentially disable integration temporarily
        LOG_ERROR("Google API authentication failed for user " + user_id, e)
        RETURN EMPTY_LIST
    CATCH APIError AS e
        LOG_ERROR("Google API call failed for user " + user_id, e)
        RETURN EMPTY_LIST
    END TRY
END FUNCTION
```

## 4. Bi-directional Synchronization (Future Consideration for MVP+)

- **Description**: While the initial MVP will likely focus on uni-directional synchronization (data flowing from external systems into TRM-OS), future versions may require bi-directional synchronization. This means TRM-OS could also create, update, or delete data in external systems based on internal events or actions.

- **Use Cases**:
    - Creating a task in an external project management tool (e.g., Google Tasks, Asana) based on a `Tension` that has been analyzed and actioned within TRM-OS.
    - Updating a contact's notes in a CRM based on interactions or `WIN`s logged in TRM-OS.
    - Posting a `Recognition` event to a team's Slack channel.

- **Key Considerations**:
    - **Conflict Resolution**: Define clear strategies for handling data conflicts if data can be updated concurrently in both TRM-OS and the external system (e.g., last-write-wins, manual intervention).
    - **Data Integrity**: Implement mechanisms to ensure data consistency across systems.
    - **Loop Prevention**: Design safeguards to prevent infinite synchronization loops where an update in one system triggers an update in the other, which in turn triggers an update back in the first system.
    - **Granular Control**: Allow users to configure which data flows are bi-directional and under what conditions.

- **Pseudo-code Example (Conceptual for Bi-directional Sync - Creating an external task)**:

```text
FUNCTION create_task_in_external_system(trmOsTaskId, targetSystemName)
    // 1. Fetch TRM-OS task details
    trm_os_task = CALL database.get_task_by_id(trmOsTaskId)
    IF trm_os_task IS NULL THEN
        LOG_ERROR("TRM-OS Task ID " + trmOsTaskId + " not found for external creation.")
        RETURN
    END IF

    // 2. Check if this task already has an external ID for the target system
    IF trm_os_task.external_ids[targetSystemName] IS NOT NULL THEN
        LOG_INFO("Task " + trmOsTaskId + " already exists in " + targetSystemName + " with ID: " + trm_os_task.external_ids[targetSystemName])
        RETURN // Or trigger an update if necessary
    END IF

    // 3. Get API client for the target system (handles auth)
    external_api_client = CALL get_api_client_for_system(targetSystemName, trm_os_task.owner_user_id) // Assuming user-specific auth

    // 4. Transform TRM-OS task data to the format expected by the external system's API
    external_task_payload = TRANSFORM_TRM_TASK_TO_EXTERNAL_FORMAT(trm_os_task, targetSystemName)

    TRY
        // 5. Call external API to create the task
        created_external_task_info = CALL external_api_client.create_task(external_task_payload)
        externalTaskId = created_external_task_info.id
        externalTaskUrl = created_external_task_info.url

        // 6. Update TRM-OS task with the external ID and URL
        CALL database.add_external_id_to_task(trmOsTaskId, targetSystemName, externalTaskId, externalTaskUrl)
        LOG_INFO("Task " + trmOsTaskId + " created in " + targetSystemName + ". External ID: " + externalTaskId)

        // 7. (Optional) Create an internal event in TRM-OS to log this action
        CALL create_internal_event(
            type = "externalTaskCreated",
            details = { "trmTaskId": trm_os_task_id, "externalSystem": target_system_name, "externalId": external_task_id }
        )
    CATCH APIError AS e
        LOG_ERROR("Failed to create task in " + targetSystemName + " for TRM Task ID " + trmOsTaskId, e)
        // Handle error, maybe queue for retry or notify user
    END TRY
END FUNCTION
```

## General Integration Principles

- **Integration Registry**: Maintain a central `IntegrationRegistry` within TRM-OS. This registry will store metadata for all active integrations, including:
    - Type of integration (e.g., Gmail, Google Sheets).
    - Authentication credentials (securely referenced).
    - Configuration settings (e.g., polling frequency, specific sheet IDs).
    - Status (e.g., `active`, `disabled`, `error`).
    - Last successful sync time (`lastSyncTime`), next scheduled sync time (`nextSyncTime`).
    - Basic error counts or logs (`errorCount`, `lastError`).

- **Data Validation**: Rigorously validate data received from external systems against expected formats and TRM-OS Pydantic models. Similarly, validate data before sending it to external systems.

- **Logging and Monitoring**: Implement comprehensive and structured logging for all integration activities. Develop monitoring dashboards or alerts to track the health and performance of integrations, highlighting errors or delays.

- **Modularity & Extensibility**: Design integration connectors as modular components (e.g., separate Python classes/modules per service). This allows for easier development, testing, maintenance, and the addition of new integrations in the future.

- **Resilience**: Build integrations to be resilient to temporary network issues or external service unavailability. Implement retry mechanisms with exponential backoff for transient errors.

- **Configuration over Code**: Where possible, make integration behaviors configurable (e.g., through UI or config files) rather than hardcoding them.

- **User Notification**: Inform users about critical integration failures or actions requiring their attention (e.g., re-authentication).
