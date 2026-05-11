workspace "eCAl Tracing System" "Description" {

    !docs "./doc/"
    !decisions "./adr/"

    !identifiers hierarchical

    configuration {
        scope "SoftwareSystem"
    }

    model {
        # Actors
        user = person "User" ""


        # External systems
        ecal = softwareSystem "eCAL System" "" "External System"
        jaeger = softwareSystem "Jaeger UI" "distributed tracing frontend" "External System"

        # Main system
        ecal_tracing = softwareSystem "eCAL Tracing" {
            description ""

            # Containers
            tracing_backend = container "Tracing-backend" {
            description "post processing and exporting"
            technology "Python"

                parser = component "Parser" {
                description "file handling & deserialization"
                technology "Python"
                }

                context_propagator = component "Context Propagator" {
                description ""
                technology "Python"
                }

                exporter = component "Exporter" {
                description ""
                technology "Python/OpenTelemetry SDK"
                }

                # Internal relationships
                context_propagator -> parser "get deserialized spans" ""
                exporter -> context_propagator "get OpenTelemetry formatted spans" ""
            }
                
            storage = container "Data directory" {
            description "storage for span/metadata files"
            technology "directory"
            }

            ecalcore = container "eCAL core" {
            description "eCAL core communication libraries and APIs"
            technology "C++"

                core = component "Core" {
                description "core communication libraries and APIs"
                technology "C++"
                }

                tracing = component "Tracing" {
                description "internal tracing library"
                technology "C++"
                }

                # Component relationships
                core -> tracing "Uses" ""
            }

            # Container relationships
            tracing_backend.parser -> storage "load serialized data" ""
            ecalcore.tracing -> storage "exports traces" ""
        }

        # System relationships
        ecal -> ecal_tracing "Produces span/metada files" ""
        user -> ecal "Runs" ""
        user -> ecal_tracing "Runs exporter on demand" ""
        user -> jaeger "Views" ""
        ecal_tracing.tracing_backend.exporter -> jaeger "Exports traces" ""
        
    }

    views {
        properties {
            "plantuml.url" "http://localhost:7777"
            "plantuml.format" "svg"
        }

        # C4 Level 1: System Context
        systemContext ecal_tracing "SystemContext" {
            title "eCAL Tracing System - System Context"
            description ""
            include *
        }

        # C4 Level 2: Container Diagram
        container ecal_tracing "Containers" {
            title "eCAL Tracing System - Container Architecture"
            description ""
            include *
        }


        # C4 Level 3: Component Diagram
        component ecal_tracing.tracing_backend "Components" {
            title "eCAL Tracing - Component Architecture"
            description ""
            include *
        }

        component ecal_tracing.ecalcore "Components-ecalcore" {
            title "eCAL Core - Component Architecture"
            description ""
            include *
        }

        # C4 Level 4: Class Diagrams (PlantUML)
        image ecal_tracing.ecalcore.tracing "TracingLibraryClassDiagram" {
            title "eCAL Tracing Library - Class Diagram"
            description ""
            plantuml puml/tracing_library.puml
        }

        styles {
            element "Element" {
                background #f7efe3
                color #2b2420
                stroke #6a5a4a
                strokeWidth 2
                shape roundedbox
                fontSize 30
            }

            element "Person" {
                background #f3d3b1
                color #4a2d1a
                stroke #b06a3c
                strokeWidth 2
                shape person
                fontSize 30
            }

            element "External System" {
                background #dce9ea
                color #2f3f42
                stroke #5b7b80
                strokeWidth 2
                fontSize 30
            }

            element "Software System" {
                background #d1bfa6
                color #2b2420
                stroke #8f6b52
                strokeWidth 2
                fontSize 30
            }

            element "Container" {
                background #f5e3c5
                color #2f2a25
                stroke #8c7b6a
                strokeWidth 2
                fontSize 30
            }

            element "Component" {
                background #fdf8f1
                color #2f2a25
                stroke #b0977b
                strokeWidth 2
                shape roundedbox
                fontSize 30
            }

            relationship "Relationship" {
                color #4a3f36
                thickness 2
                fontSize 24
                dashed false
            }
        }
    }

}
