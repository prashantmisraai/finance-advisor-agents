import os


def main() -> None:
    print("GROQ_API_KEY set:", bool(os.getenv("GROQ_API_KEY")))
    print("GROQ_MODEL:", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))

    try:
        import langchain_groq  # noqa: F401

        print("langchain-groq installed: yes")
    except ImportError as exc:
        print("langchain-groq installed: no")
        print("error:", exc)

    try:
        import langgraph  # noqa: F401

        print("langgraph installed: yes")
    except ImportError as exc:
        print("langgraph installed: no")
        print("error:", exc)


if __name__ == "__main__":
    main()
