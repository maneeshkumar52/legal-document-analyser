import asyncio, sys
sys.path.insert(0, '.')

async def main():
    print("=== Legal Document Analyser - End-to-End Demo ===\n")

    # Test 1: Hierarchical Chunker (no Azure needed)
    from src.hierarchical_chunker import HierarchicalChunker, DocumentChunk
    chunker = HierarchicalChunker()

    sample_contract = """# SERVICE AGREEMENT

ARTICLE 1 - PARTIES AND SCOPE
This Service Agreement ("Agreement") is entered into between TechCorp Ltd ("Provider")
and Contoso Financial plc ("Client"). The Provider agrees to deliver cloud infrastructure
services including 99.5% uptime SLA, 24/7 monitoring, and dedicated support.

ARTICLE 2 - FEES AND PAYMENT
The Client shall pay £15,000 per month for the Standard tier. Payment is due within 30
days of invoice. Late payments incur 2% monthly interest. Annual contract with 90-day
termination notice required.

ARTICLE 3 - DATA PROTECTION
Provider shall comply with UK GDPR and DPA 2018. Data shall not be transferred outside
the UK/EEA without written consent. Provider shall notify Client of any breach within
72 hours. Data Processing Agreement (DPA) forms Schedule A of this Agreement.

SECTION 4 - LIABILITY AND INDEMNIFICATION
Provider's total liability shall not exceed 12 months' fees (£180,000). Provider
indemnifies Client against third-party IP infringement claims. Force majeure events
excuse performance for up to 30 days.

CLAUSE 5 - TERMINATION
Either party may terminate for material breach with 30 days written notice. Client may
terminate for convenience with 90 days notice and payment of outstanding fees. Provider
may suspend services for non-payment after 15 days written notice.
"""

    # chunk() takes (text, contract_id, document_title)
    all_chunks = chunker.chunk(sample_contract, contract_id="service_agreement_demo", document_title="Service Agreement")
    level1 = [c for c in all_chunks if c.chunk_type == "section_summary"]
    level2 = [c for c in all_chunks if c.chunk_type == "paragraph"]

    print(f"Hierarchical Chunker:")
    print(f"  Level 1 (section summaries): {len(level1)} chunks")
    print(f"  Level 2 (paragraphs): {len(level2)} chunks")
    if level1:
        print(f"  Sample L1 chunk: {level1[0].content[:100]}...")
    if level2:
        print(f"  Sample L2 chunk: {level2[0].content[:100]}...")

    # Test 2: Sample contracts
    import os
    contracts_path = "indexer/sample_contracts"
    if os.path.exists(contracts_path):
        files = os.listdir(contracts_path)
        print(f"\nSample contracts: {len(files)} documents")
        for f in files:
            filepath = os.path.join(contracts_path, f)
            with open(filepath, 'r') as fp:
                content = fp.read()
            print(f"  - {f}: {len(content)} chars, {len(content.splitlines())} lines")

    # Test 3: Run the existing unit tests
    print(f"\n--- Running unit tests (no Azure needed) ---")
    import subprocess
    result = subprocess.run(
        ['/Users/maneeshkumar/Documents/Agentic_Book_Proj/.venv/bin/python', '-m', 'pytest', 'tests/test_chunker.py', '-v', '--tb=short'],
        capture_output=True, text=True, cwd='.'
    )
    output = result.stdout
    print(output[-1500:] if len(output) > 1500 else output)
    if result.returncode != 0:
        print(result.stderr[-500:])

    print("\n=== Legal Document Analyser: Hierarchical chunking and contract analysis ready ===")

asyncio.run(main())
