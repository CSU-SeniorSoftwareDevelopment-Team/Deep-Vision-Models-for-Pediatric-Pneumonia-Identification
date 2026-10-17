# DeepImage
### Local Healthcare AI Infrastructure and Medical Image Analysis

**Columbus State University · Fall 2026**

DeepImage is an academic research and software engineering project focused on developing a locally deployed AI platform for healthcare environments. The system uses a client-server architecture to provide AI-powered image analysis through a service hosted within a hospital, doctor's office, or other healthcare facility.

Rather than requiring individual users to run their own AI models, DeepImage is designed to provide a shared AI service that authorized healthcare personnel can access through client applications. The local server handles image-processing requests and AI inference, providing a foundation for medical image analysis, in-house research, and future AI services.

The broader vision extends beyond a standalone software application. DeepImage explores a service-based business model in which healthcare facilities operate local AI infrastructure while a company-managed backend supports software updates, new capabilities, and continued platform development.

The goal is to make AI infrastructure more accessible to healthcare organizations by combining local processing, cost-effective AI models, flexible research capabilities, and ongoing software services.

> **Disclaimer:** DeepImage is an academic research and development project. It is not a clinically validated medical diagnostic device and is not intended to replace qualified healthcare professionals or their clinical judgment.

---

## Table of Contents

- [About the Project](#about-the-project)
- [System Architecture](#system-architecture)
- [Local Healthcare AI Service](#local-healthcare-ai-service)
- [Client Applications](#client-applications)
- [Company-Managed Backend](#company-managed-backend)
- [Security Architecture](#security-architecture)
- [AI and Medical Image Analysis](#ai-and-medical-image-analysis)
- [Research and Model Development](#research-and-model-development)
- [Performance Evaluation](#performance-evaluation)
- [Business and Service Model](#business-and-service-model)
- [Technology Stack](#technology-stack)
- [Project Goals](#project-goals)
- [Project Status](#project-status)
- [Academic Affiliation](#academic-affiliation)
- [Team](#team)
- [References](#references)

---

## About the Project

Healthcare organizations have growing opportunities to use artificial intelligence for research, image analysis, and other computational tasks. However, deploying AI can introduce challenges involving infrastructure costs, data privacy, model maintenance, computing requirements, and dependence on external cloud services.

DeepImage explores an alternative approach: **locally deployed AI infrastructure delivered as a service**.

A healthcare facility can host a DeepImage server within its own environment, allowing authorized users to access AI capabilities through client applications. The server provides a shared processing resource, while the broader platform is designed to support the introduction of additional models, research tools, and software capabilities.

The initial AI application focuses on medical image classification, including research into pediatric pneumonia classification from chest X-ray images. However, the platform is not intended to be limited to a single model or medical application.

By separating the AI service, client applications, networking, and future management services, DeepImage establishes an architecture that can evolve as additional requirements and use cases emerge.

The project emphasizes four primary areas:

- **Local AI processing:** Providing AI inference within the healthcare facility's environment.
- **Secure connectivity:** Restricting access through private networking, account-associated IP allowlisting, and TLS-secured communications.
- **Research flexibility:** Exploring affordable AI models that healthcare organizations can evaluate, train, or adapt for their own research.
- **Long-term service delivery:** Supporting a managed platform that can receive software updates and additional capabilities over time.

## System Architecture

DeepImage follows a modular client-server architecture supported by a broader company-managed service model.

The architecture separates responsibilities into three primary components.

### 1. Local Healthcare AI Server

The local server is the central AI-processing component deployed within a healthcare facility.

Its intended responsibilities include:

- Receiving image-processing requests from connected clients.
- Running AI inference using available neural network models.
- Managing the server-side components required for image processing.
- Handling client connections and communication.
- Providing a shared AI resource for authorized users.
- Supporting future model-management and research workflows.
- Multi-concurrent users with security.
- Cost reduction for the research and AI medical tools.

By centralizing inference, DeepImage allows multiple authorized clients to access AI capabilities without each workstation needing to host an independent copy of the model.

The local server is intended to operate within the facility's network, reducing the need to transmit every image-processing request to an external cloud inference service.

### 2. Client Applications

Client applications provide the interface through which users interact with the local AI service.

The intended workflow allows authorized healthcare personnel to connect to the server, submit images for processing, and receive the resulting predictions.

The client-server separation allows the user interface and AI-processing components to be developed and maintained independently.

This architecture also establishes a foundation for supporting multiple workstations and different client applications using the same server-side AI resources.

### 3. Company-Managed Backend Service

The broader DeepImage platform is designed to include a company-managed backend responsible for supporting the continuing development and maintenance of local installations.

The intended service model includes:

- Distribution of software updates.
- Delivery of new platform features.
- Support for introducing additional AI capabilities.
- Continued development and maintenance of the platform.
- Potential coordination of model and software versions across deployments.

This separates the healthcare facility's local AI environment from the services used to maintain and extend the platform.

The company-managed service is intended to support ongoing platform development without requiring the AI inference process to depend entirely on an external cloud service.

The precise update mechanisms, remote management features, and deployment controls depend on the implemented components of the system.

### High-Level Architecture

```text
              DEEPIMAGE COMPANY SERVICES
          +--------------------------------+
          | Software Updates               |
          | New Platform Features          |
          | Future AI Capabilities         |
          +---------------+----------------+
                          |
                Managed Update Channel
                          |
                          v
+---------------------------------------------------+
|            HEALTHCARE FACILITY                   |
|                                                   |
|  +---------------------------------------------+  |
|  |          LOCAL DEEPIMAGE SERVER             |  |
|  |                                             |  |
|  |  AI Inference and Image Processing          |  |
|  |  Server-Side Model Execution                |  |
|  |  Client Connection Management               |  |
|  |  User-Bound IP Allowlist                    |  |
|  +----------------------+----------------------+  |
|                         |                         |
|                 TCP + TLS                         |
|                         |                         |
|             Private Tailscale Network             |
|                         |                         |
|               +---------+---------+               |
|               |                   |               |
|               v                   v               |
|        +-------------+     +-------------+        |
|        |  Client A   |     |  Client B   |        |
|        | Workstation |     | Workstation |        |
|        +-------------+     +-------------+        |
|                                                   |
+---------------------------------------------------+
```

*This diagram illustrates the intended deployment model. It does not imply that every management, update, or research component is already implemented.*

---

## Local Healthcare AI Service

An important goal of DeepImage is to make AI capabilities accessible through infrastructure operated within a healthcare facility.

Instead of requiring every workstation to run its own model or sending every request to an external AI provider, the facility can use a shared local server to process requests from authorized clients.

This model offers several potential advantages.

### Local Processing

Images can be submitted to a server operating within the facility's network. This can reduce dependence on external inference infrastructure and limit the need to transmit medical images to third-party AI services.

Local deployment does not automatically guarantee privacy or regulatory compliance. Data handling depends on the complete system configuration and operational policies.

### Shared Infrastructure

Multiple authorized users can access the same AI service, reducing the need to install and maintain a separate inference environment on every workstation.

### Cost-Conscious Deployment

DeepImage emphasizes investigating smaller, more efficient models that can run on relatively inexpensive hardware.

The objective is to explore whether useful AI research and inference can be performed without requiring every facility to invest in expensive, dedicated AI infrastructure.

Actual hardware requirements and operating costs will depend on model size, workload, and performance requirements.

### Flexible Research

The platform is intended to support experimentation with different models and datasets. Healthcare facilities could potentially evaluate existing models, develop their own models, or adapt models for research purposes.

The availability of local training, model customization, and dataset-management functionality depends on the implemented capabilities of each deployment.

---

## Client Applications

The DeepImage client-server design separates user interaction from AI processing.

Clients communicate with the local server to request image analysis rather than executing the complete inference workflow independently.

The intended client workflow is:

1. An authorized user opens the client application.
2. The client establishes a connection to the local DeepImage server.
3. The user submits an image for processing.
4. The server processes the request using an available AI model.
5. The client receives the server's response and presents the result.

This design provides a foundation for centralized AI processing and independent development of the client interface.

Additional client features, such as user administration, result history, research dashboards, and model selection, can be developed as requirements evolve.
User features such as chamge password, name, bound IP can be found un the UI via the dashboard. 

---

## Future Company-Managed Backend Services: 

DeepImage is intended to operate as more than a one-time software installation.

The company-managed backend represents the service layer responsible for delivering continued platform development to local deployments.

The long-term objective is to allow healthcare facilities to maintain local AI-processing capabilities while receiving software improvements and additional features through a managed update process.

Potential capabilities include:

- Versioned software releases.
- Controlled delivery of new features.
- Additional AI models and processing capabilities.
- Deployment and compatibility management.
- Maintenance and technical support.

The update mechanism must be designed so that only authorized software and configurations can be installed. Depending on the implementation, this may involve signed updates, authenticated service connections, version verification, and controlled rollout procedures.

The company-managed backend is intended to complement the local AI server rather than replace it as the primary inference environment.

---

## Security Architecture

Security is a core consideration in the DeepImage architecture because the intended deployment involves healthcare environments and potentially sensitive medical information.

The system uses multiple layers of network and communication security, including Tailscale VPN connectivity, server-side IP allowlisting associated with user accounts, and TLS-secured TCP communication.

The design follows a defense-in-depth approach, with the objective of restricting unauthorized access and protecting data in transit.

### TCP and TLS

DeepImage uses TCP for reliable transport between the client and server, with TLS providing encryption and authentication over the connection.

The communication layer is designed around the following principles:

- Encrypted communication between clients and the server.
- Certificate-based authentication and certificate validation.
- A private certificate authority where configured.
- Connection monitoring and handling of network failures.
- Support for multiple concurrent client connections.

TCP provides transport reliability; it does not provide encryption by itself. TLS provides the cryptographic protection for the connection when configured and validated correctly.

Certificate validation, trust configuration, private-key protection, and certificate lifecycle management are important to maintaining the security of this layer.

### Tailscale VPN

DeepImage uses Tailscale to provide private network connectivity between authorized devices and the local AI server.

Tailscale establishes a private network environment that can restrict access to participating devices according to the tailnet's configuration and access policies.

The VPN layer provides an additional boundary around the service, reducing direct exposure to the public internet when the deployment is configured to use private connectivity.

Tailscale access controls and server-side authorization remain important: being connected to a private network should not automatically grant unrestricted access to the AI service.

### User-Bound IP Allowlisting

The server maintains a list of allowed IP addresses associated with user accounts.

Incoming connections can be checked against the configured allowlist to determine whether the connection originates from an approved network address associated with the account.

This mechanism provides an additional restriction on which endpoints may communicate with the server.

The intended controls include:

- Maintaining configured allowlisted IP addresses on the server.
- Associating allowlist entries with user accounts.
- Checking incoming connection addresses against the configured entries.
- Rejecting connections that do not meet the server's network restrictions.

Tailscale addresses are used within the private network and should be distinguished from public static IP addresses.

An IP address is an attribute of a network endpoint, not proof of a person's identity. Account authentication and application-level authorization are still necessary to establish which user is accessing the service and what that user is permitted to do.

### Zero-Trust Security Objectives

DeepImage's security design aims to follow zero-trust principles by avoiding implicit trust based solely on network location.

The intended approach combines:

- Private VPN connectivity through Tailscale.
- Server-side IP allowlisting associated with user accounts.
- TLS-secured communications.
- Certificate validation.
- User authentication and application-level authorization.

A complete zero-trust implementation also requires appropriate identity verification, resource-level access controls, credential management, and monitoring.

These controls must be implemented and verified as part of the complete deployment. Many features of this are rolled out into the project, but are not fully implemented for end product medical use.

### Healthcare Data Protection

Local processing can reduce the need to send medical images to external inference providers, but it does not automatically make a deployment HIPAA-compliant or otherwise suitable for clinical use.

A production healthcare deployment would also need to address applicable requirements for access control, audit logging, data retention, secure storage, backups, incident response, and operational security.

DeepImage is an academic project, and its security and privacy properties must be evaluated against the requirements of any intended real-world deployment.

---

## AI and Medical Image Analysis

The initial AI research application focuses on pediatric pneumonia classification using chest X-ray images.

The AI component uses Python and PyTorch to develop and evaluate neural network models for image classification.

The objective is to investigate how a model can analyze an input image and generate a prediction based on patterns learned from its training data.

The research application provides an initial use case for the larger DeepImage platform, demonstrating how an AI model can be exposed through a server-based service.

Potential areas of development include:

- Image loading and preprocessing.
- Neural network training and inference.
- Training and evaluation dataset management.
- Classification performance analysis.
- Model efficiency and computational requirements.
- Integration of model inference with the client-server workflow.

The broader platform is intended to remain extensible so that additional models and AI applications can be introduced without requiring the entire architecture to be redesigned.

Predictions generated by the current research model should not be interpreted as confirmed diagnoses.

---

## Research and Model Development

DeepImage explores the potential for healthcare facilities to use relatively inexpensive AI models for in-house research.

The long-term direction includes allowing organizations to investigate available models, evaluate their performance on relevant datasets, and potentially train or adapt models for their own research objectives.

This creates a distinction between the shared AI infrastructure and the models that operate on it.

The platform can provide the infrastructure for serving models, while model development and evaluation remain separate research activities.

Potential future research areas include:

### Model Efficiency

Investigating smaller neural networks and lower-cost hardware to understand the trade-offs between computational requirements and model performance.

### Dataset Management

Exploring workflows for preparing, organizing, and evaluating labeled datasets for model development.

### Model Training and Customization

Investigating whether healthcare facilities can train models or adapt existing models to their own research needs.

Any such capability would require appropriate data-management controls, model compatibility, and safeguards against unintended changes to production deployments.



---

## Performance Evaluation

The initial medical image classification application can be evaluated using established machine learning metrics.

- **Accuracy:** The proportion of predictions that are correct.
- **Precision:** The proportion of positive predictions that are correct.
- **Recall (Sensitivity):** The proportion of actual positive cases identified by the model.
- **Specificity:** The proportion of actual negative cases correctly identified.
- **F1 Score:** The harmonic mean of precision and recall.
- **Confusion Matrix:** A breakdown of correct and incorrect classifications.

For pneumonia classification, sensitivity and specificity are particularly relevant because false-negative and false-positive predictions have different implications.

If the system is extended to object detection or image localization, additional metrics such as mean average precision (mAP) may be appropriate. These metrics are not necessarily relevant to a basic binary classification task.

Future evaluation of the platform itself may also consider:

- Request-processing latency.
- Concurrent client handling.
- Server resource utilization.
- Network reliability.
- Model inference throughput.
- Performance on lower-cost hardware.

Machine learning metrics alone do not establish clinical safety. Clinical deployment would require suitable validation, assessment of dataset limitations, and compliance with applicable regulatory requirements.

---

## Business and Service Model

DeepImage is being developed with a broader business model in mind: providing locally deployed AI infrastructure supported by an ongoing software service.

Rather than treating AI as a one-time software purchase, the concept is to provide healthcare organizations with a local AI environment that can be maintained and expanded over time.

### Local Infrastructure

The healthcare facility operates its own local AI server and provides access to AI capabilities through its internal network.

This supports shared AI processing and creates a foundation for in-house research and experimentation.

### Managed Platform Services

The platform provider continues to develop the software and delivers new capabilities through a managed service relationship.

This may include software updates, additional AI models, new features, and ongoing maintenance.

### Research Flexibility

The platform aims to provide organizations with a foundation for experimenting with affordable AI models and, where supported, training or adapting models for their own research.

This can give facilities more flexibility in how they evaluate and use AI than a model tied exclusively to a single external inference provider.

### Long-Term Vision

The long-term vision is to combine local infrastructure with continuing platform development.

This model is intended to make AI services more accessible while allowing the platform to evolve as new models, research needs, and deployment requirements emerge.

The commercial model, service agreements, update infrastructure, and production support requirements remain subject to further development.

---

## Technology Stack

DeepImage is primarily developed using the following technologies:

| Technology | Purpose |
|---|---|
| Python | AI development and backend implementation |
| PyTorch | Neural network training and inference |
| TCP sockets | Client-server transport |
| TLS/SSL | Encrypted communication and certificate-based authentication |
| Tailscale | Private VPN connectivity |
| Computer vision | Image analysis and preprocessing |
| [GUI] Tkinter  | Client and administrative interfaces, as applicable |

Additional libraries and infrastructure components may be introduced as the system evolves.

---

## Project Goals

The primary goals of DeepImage are to:

1.  Develop a modular client-server architecture for delivering AI inference as a shared local service.
2.  Explore local AI deployment within hospital and medical office environments.
3.  Investigate cost-effective models that can operate on accessible computing hardware.
4.  Develop a medical image classification research application using PyTorch.
5.  Establish secure client-server communication using TLS and private network connectivity.
6.  Restrict network access through Tailscale and server-side user-associated IP allowlisting.
7.  Explore workflows for local model experimentation, training, and evaluation.
8.  Develop a foundation for managed software updates and additional platform capabilities.
9.  Investigate a sustainable service model that combines local infrastructure with ongoing software development.
10. UI/UX desgine that allows for easy and quick use to obtain rapid medical results.

---

## Project Status

**Currently in Development**

DeepImage is an ongoing academic research and software engineering project at Columbus State University for the Fall 2026 semester.

The project has evolved from an initial AI image-classification application into a broader client-server platform designed around local healthcare AI infrastructure.

Current development focuses on the server-based architecture, client communication, AI service integration, and network security components.

The broader platform vision includes managed software updates, additional AI capabilities, and support for healthcare research workflows.

The availability of individual features depends on their implementation and testing. Planned capabilities should not be interpreted as completed or production-ready functionality.

---

## Academic Affiliation

**Columbus State University**

**Semester:** Fall 2026

**Development Period:** August 2026 – December 2026

The project is being developed as a collaborative student research and software engineering effort.

---

## Team

**Team Lead:** Steven Andrews II

**Project Team:**

- **Steven Andrews II** — Team Lead / Development Lead
- **Bhavik Patel** — Research and AI
- **Jhonathan Falls** — Research and AI
- **Ahumada Camillie** — Research, AI, and UI

---

## References

1. Center for Policy Impact — *From Pixels to Prognosis: How Artificial Intelligence (AI) Analyzes Medical Images for Childhood Pneumonia Detection*  
   https://centerforpolicyimpact.org/2024/08/10/from-pixels-to-prognosis-how-artificial-intelligence-ai-analyzes-medical-images-for-childhood-pneumonia-detection/

2. National Library of Medicine / PubMed Central  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10047666/

3. arXiv — Research paper  
   https://arxiv.org/abs/2507.09759

---

*DeepImage is a developing platform for local healthcare AI services, secure client-server communication, and accessible medical AI research.*