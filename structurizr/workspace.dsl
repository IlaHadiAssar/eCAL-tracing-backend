workspace "Name" "Description" {

    !adrs "./adr/"

    !identifiers hierarchical

    model {
        # External actors
        dev = person "Developer/DevOps" "Operates and monitors the system"

        # External systems
        ecal = softwareSystem "eCAL Core" "Event Communication Abstraction Layer - generates publisher/subscriber spans and topic metadata" "External System"

        # Main system
        backend = softwareSystem "eCAL Tracing Backend" {
            description "OpenTelemetry tracing backend for eCAL pub/sub instrumentation"

            # Containers
            collector = container "Data Collector" {
                description "Discovers and loads span/metadata JSONL files from data directory"
                technology "Python"

                fileDiscoverer = component "File Discoverer" {
                    description "Discovers span and metadata JSONL files using glob patterns"
                    technology "Python glob"
                }

                fileReader = component "File Reader" {
                    description "Reads and parses JSON/JSONL files from filesystem"
                    technology "Python json"
                }

                dataValidator = component "Data Validator" {
                    description "Validates span and metadata schema before processing"
                    technology "Python"
                }

                fileDiscoverer -> fileReader "Provides file paths"
                fileReader -> dataValidator "Provides parsed records"
            }

            mapper = container "Span Mapper" {
                description "Maps eCAL publisher/subscriber spans to OpenTelemetry trace model with context propagation"
                technology "Python"
                tags "Core Logic"

                fileLoader = component "JSON File Loader" {
                    description "Loads span and metadata JSONL files"
                    technology "Python"
                }

                metadataBuilder = component "Metadata Builder" {
                    description "Constructs lookup maps of topic metadata"
                    technology "Python"
                }

                enumDecoder = component "Enum Decoder" {
                    description "Decodes eCAL enums: operation types, directions, transport layers"
                    technology "Python"
                }

                spanCreator = component "Span Creator" {
                    description "Maps eCAL spans to OpenTelemetry with context propagation"
                    technology "Python"
                }

                contextPropagator = component "Context Propagator" {
                    description "Maintains context links: publish → receive → callback"
                    technology "Python"
                }

                # Component relationships
                fileLoader -> enumDecoder "Decodes operation types"
                fileLoader -> metadataBuilder "Provides raw data"
                metadataBuilder -> spanCreator "Supplies metadata context"
                spanCreator -> contextPropagator "Links span contexts"
                contextPropagator -> spanCreator "Adds parent/child references"
            }

            tracer = container "Tracer Provider" {
                description "Manages OpenTelemetry SDK and builds unified trace hierarchy"
                technology "OpenTelemetry Python SDK"
                tags "Core Logic"

                resourceFactory = component "Resource Factory" {
                    description "Creates OTel Resource with service metadata"
                    technology "OpenTelemetry SDK"
                }

                tracerFactory = component "Tracer Factory" {
                    description "Instantiates TracerProvider with resource"
                    technology "OpenTelemetry SDK"
                }

                consoleExporter = component "Console Exporter" {
                    description "Debug exporter that prints spans to console"
                    technology "Python/Custom"
                }

                otlpExporter = component "OTLP HTTP Exporter" {
                    description "Exports spans to Jaeger via OTLP HTTP"
                    technology "OpenTelemetry SDK"
                }

                processorManager = component "Processor Manager" {
                    description "Manages SimpleSpanProcessor and BatchSpanProcessor"
                    technology "OpenTelemetry SDK"
                }

                # Component relationships
                resourceFactory -> tracerFactory "Configures with service metadata"
                tracerFactory -> processorManager "Registers span processors"
                processorManager -> consoleExporter "Routes spans to console"
                processorManager -> otlpExporter "Routes spans to OTLP"
            }

            exporter = container "OTLP Exporter" {
                description "Exports traces to Jaeger via OTLP HTTP protocol"
                technology "OpenTelemetry OTLP HTTP Exporter"

                batchProcessor = component "Batch Processor" {
                    description "Batches spans for efficient export to reduce overhead"
                    technology "OpenTelemetry SDK"
                }

                httpTransport = component "HTTP Transport" {
                    description "Sends batched span data via HTTP/JSON to Jaeger"
                    technology "OpenTelemetry OTLP HTTP"
                }

                consoleDebugger = component "Console Debugger" {
                    description "Routes spans to console for real-time debugging"
                    technology "Python/Custom"
                }

                batchProcessor -> httpTransport "Sends batch"
                batchProcessor -> consoleDebugger "Sends copy for debug"
            }

            # Internal relationships
            collector -> mapper "Supplies eCAL span data"
            mapper -> tracer "Creates OTel spans with context"
            tracer -> exporter "Sends trace data"
        }

        # External systems continued
        jaeger = softwareSystem "Jaeger" "Distributed tracing backend - receives and visualizes traces" "External System"

        # System relationships
        ecal -> backend.collector "Produces span/metadata JSON files"
        dev -> backend "Configures and operates via CLI"
        dev -> jaeger "Views traces via UI"
        backend -> jaeger "Exports traces on port 4318"
    }

    views {
        # C4 Level 1: System Context
        systemContext backend "SystemContext" {
            title "eCAL Tracing Backend - System Context"
            description "Context diagram showing eCAL tracing backend, eCAL Core, and Jaeger"
            include *
            autolayout lr
        }

        # C4 Level 2: Container Diagram
        container backend "Containers" {
            title "eCAL Tracing Backend - Container Architecture"
            description "Container diagram showing data flow from file loading through span mapping to Jaeger export"
            include *
            autolayout lr
        }

        # C4 Level 3: Component Diagrams
        component backend.mapper "MapperComponents" {
            title "Span Mapper - Component Diagram"
            description "Shows how the Span Mapper breaks down JSON loading, metadata building, enum decoding, and OpenTelemetry span creation with context propagation"
            include *
            autolayout lr
        }

        component backend.tracer "TracerComponents" {
            title "Tracer Provider - Component Diagram"
            description "Shows how the Tracer Provider manages OpenTelemetry SDK initialization, exporters, and span processors for both console and OTLP output"
            include *
            autolayout lr
        }

        component backend.collector "CollectorComponents" {
            title "Data Collector - Component Diagram"
            description "Shows how the Data Collector discovers, reads, and validates JSONL files for processing"
            include *
            autolayout lr
        }

        component backend.exporter "ExporterComponents" {
            title "OTLP Exporter - Component Diagram"
            description "Shows how the OTLP Exporter batches spans and sends them to Jaeger via HTTP while also debugging to console"
            include *
            autolayout lr
        }

        styles {
            element "Element" {
                color #438dd5
                stroke #3c7fc0
                strokeWidth 3
                shape roundedbox
                fontSize 14
                icon https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/python.svg
            }

            element "Person" {
                color #08427b
                stroke #073461
                shape person
                fontSize 14
            }

            element "External System" {
                color #999999
                stroke #666666
                fontSize 14
            }

            element "Core Logic" {
                color #85bbf0
                stroke #3c7fc0
                strokeWidth 4
            }

            element "Component" {
                color #65c0f5
                stroke #3c7fc0
                strokeWidth 2
                shape roundedbox
                fontSize 12
            }

            relationship "Relationship" {
                thickness 2
                fontSize 12
                dashed false
            }
        }
    }

    configuration {
        scope softwaresystem
    }

}
