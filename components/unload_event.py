import streamlit as st
import streamlit.components.v1 as components

def unload_event():
    # JavaScript to detect window unload event
    unload_js = """
    <script>
    window.addEventListener("beforeunload", function (e) {
        // Custom event to notify Streamlit of the unload event
        var event = new CustomEvent("saveThreads", {});
        document.dispatchEvent(event);
    });
    </script>
    """
    components.html(unload_js, height=0, width=0)

unload_event()
