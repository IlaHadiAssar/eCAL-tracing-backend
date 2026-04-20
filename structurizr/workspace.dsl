workspace "eCAl Tracing System" "Description" {

    !docs "./doc/"
    !decisions "./adr/"

    !identifiers hierarchical

    configuration {
        scope "SoftwareSystem"
    }

    model {
        # Actors
        owner = person "eCAL System Owner" "Operates some system with eCAL usage"
        dev = person "eCAL Developer" "Develops eCAL and offers support to eCAL system Owners"

        # External systems
        ecal = softwareSystem "eCAL User System" "Some system which uses eCAL" "External System"

        # Main system
        backend = softwareSystem "eCAL Tracing Backend" {
            description "OpenTelemetry tracing backend for eCAL pub/sub context propagation and exporting"

            # Containers
            main = container "src.main" {
            description "the main python module"
            technology "Python"

                collector = component "Data Collector" {
                description "Discovers and loads span/metadata JSONL files from data directory"
                technology "Python"
                }

                mapper = component "Span Mapper" {
                description "Maps eCAL publisher/subscriber spans to OpenTelemetry trace model with context propagation"
                technology "Python"
                }

                exporter = component "OTLP Exporter" {
                description "Manages OpenTelemetry SDK and builds unified trace hierarchy and exports traces to Jaeger via OTLP HTTP protocol"
                technology "OpenTelemetry Python HTTP"
                }

                # Internal relationships
                collector -> mapper "Supplies eCAL span data" "Python"
                mapper -> exporter "Creates OTel spans with context" "OpenTelemetry SDK"
            }
                
            storage = container "data/" {
            description "a directory which stores data exported from eCAL in JSON files"
            technology "directory"
            }

            ecalcore = container "ecal core" {
            description "ecal core communication libraries and APIs"
            technology "C++"

                core = component "Core" {
                description "ecals core communication libraries and APIs"
                technology "C++"
                }

                tracing = component "Tracing" {
                description "eCALs internal tracing library"
                technology "C++"
                }

                # Component relationships
                core -> tracing "Uses" "C++"
            }

            # Container relationships
            main.collector -> storage "loads JSON files from storage" "JSONL files"
            ecalcore.tracing -> storage "exports traces as JSON" "JSONL files"
        }

        # External systems continued
        jaeger = softwareSystem "Jaeger" "Distributed tracing frontend - receives and visualizes traces" "External System"

        # System relationships
        ecal -> backend "Produces span/metadata JSON files" "JSONL files"
        owner -> ecal "Configures and operates System" "eCAL Suite"
        owner -> backend "Runs exporter on demand" "CLI"
        owner -> jaeger "Views traces via UI" "Web UI"
        dev -> backend "Runs exporter on demand" "CLI"
        dev -> jaeger "Views traces via UI" "Web UI"
        backend.main.exporter -> jaeger "Exports traces on port 4318" "OTLP HTTP"
        
    }

    views {
        properties {
            "plantuml.url" "http://localhost:7777"
            "plantuml.format" "svg"
        }

        # C4 Level 1: System Context
        systemContext backend "SystemContext" {
            title "eCAL Tracing System - System Context"
            description "Context diagram showing eCAL tracing system, eCAL System, and Jaeger"
            include *
        }

        # C4 Level 2: Container Diagram
        container backend "Containers" {
            title "eCAL Tracing System - Container Architecture"
            description "Container diagram showing data flow from file loading through span mapping to Jaeger export"
            include *
        }


        # C4 Level 3: Component Diagram
        component backend.main "Components" {
            title "eCAL Tracing Backend - Component Architecture"
            description "Container diagram showing data flow from file loading through span mapping to Jaeger export"
            include *
        }

        component backend.ecalcore "Components-ecalcore" {
            title "eCAL Core - Component Architecture"
            description "Component diagram for eCAL core container"
            include *
        }

        # C4 Level 4: Class Diagrams (PlantUML)
        image backend.main.collector "CollectorClassDiagram" {
            title "Data Collector - Class Diagram"
            description "Classes responsible for file discovery, JSONL loading, and metadata validation"
            plantuml puml/collector_classes.puml
        }

        image backend.main.mapper "MapperClassDiagram" {
            title "Span Mapper - Class Diagram"
            description "Classes for loading spans, building metadata lookups, decoding enums, creating OTel spans, and propagating context"
            plantuml puml/mapper_classes.puml
        }

        image backend.main.exporter "ExporterClassDiagram" {
            title "Tracer Provider & Exporter - Class Diagram"
            description "Classes for resource creation, tracer setup, console debugging, and OTLP HTTP export to Jaeger"
            plantuml puml/tracer_exporter_classes.puml
        }

        image backend.ecalcore.tracing "TracingLibraryClassDiagram" {
            title "eCAL Tracing Library - Class Diagram"
            description "Classes and enumerations of the eCAL tracing library including CSpan, CTraceProvider, CTracingWriter, and supporting data structures"
            plantuml puml/tracing_library.puml
        }

        styles {
            element "Element" {
                background #f7efe3
                color #2b2420
                stroke #6a5a4a
                strokeWidth 2
                shape roundedbox
                fontSize 24
            }

            element "Person" {
                background #f3d3b1
                color #4a2d1a
                stroke #b06a3c
                strokeWidth 2
                shape person
                fontSize 24
            }

            element "External System" {
                background #dce9ea
                color #2f3f42
                stroke #5b7b80
                strokeWidth 2
                fontSize 24
            }

            element "Software System" {
                background #d1bfa6
                color #2b2420
                stroke #8f6b52
                strokeWidth 2
                fontSize 24
            }

            element "Container" {
                background #f5e3c5
                color #2f2a25
                stroke #8c7b6a
                strokeWidth 2
                fontSize 24
            }

            element "Component" {
                background #fdf8f1
                color #2f2a25
                stroke #b0977b
                strokeWidth 2
                shape roundedbox
                fontSize 24
            }

            relationship "Relationship" {
                color #4a3f36
                thickness 2
                fontSize 18
                dashed false
            }
        }
    }

}
