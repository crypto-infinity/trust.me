class ReportAgent:
    async def run(self, checked_data, score, details):
        # Genera un report markdown semplice
        report = f"""# Trust.me Report\n\n**Score di fiducia:** {score}/100\n\n## Dettagli\n{details}\n\n---\n\n## Dati analizzati\n{checked_data}\n"""
        return report
