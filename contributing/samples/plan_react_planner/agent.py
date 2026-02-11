# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example demonstrating PlanReActPlanner for structured planning and reasoning.

This sample shows how PlanReActPlanner helps agents:
1. Create an explicit plan before taking actions
2. Reason between tool executions
3. Separate planning, reasoning, actions, and final answers
4. Adapt plans based on tool results (replanning)

The example uses a research assistant that needs to gather information,
analyze it, and provide a comprehensive answer - a perfect use case for
structured planning.
"""

from __future__ import annotations

import json
from typing import Any

from google.adk.agents.llm_agent import Agent
from google.adk.planners.plan_re_act_planner import PlanReActPlanner
from google.adk.tools.tool_context import ToolContext


# Simulated tools for demonstration
def search_papers(query: str, max_results: int = 3) -> str:
  """Search for academic papers on a topic.

  Args:
    query: The search query for papers.
    max_results: Maximum number of results to return.

  Returns:
    JSON string with paper titles, authors, and abstracts.
  """
  # Simulated paper database
  papers_db = {
      'machine learning': [
          {
              'title': 'Deep Learning for Computer Vision',
              'authors': 'Smith et al.',
              'year': 2023,
              'abstract': 'A comprehensive survey of deep learning techniques for computer vision tasks.',
              'citations': 450,
          },
          {
              'title': 'Transformer Architectures in NLP',
              'authors': 'Johnson et al.',
              'year': 2022,
              'abstract': 'Analysis of transformer models and their applications in natural language processing.',
              'citations': 890,
          },
          {
              'title': 'Reinforcement Learning: Recent Advances',
              'authors': 'Chen et al.',
              'year': 2024,
              'abstract': 'Overview of recent breakthroughs in reinforcement learning algorithms.',
              'citations': 120,
          },
      ],
      'quantum computing': [
          {
              'title': 'Quantum Algorithms for Optimization',
              'authors': 'Williams et al.',
              'year': 2023,
              'abstract': 'Novel quantum algorithms for solving optimization problems.',
              'citations': 230,
          },
          {
              'title': 'Error Correction in Quantum Systems',
              'authors': 'Lee et al.',
              'year': 2024,
              'abstract': 'Advances in quantum error correction techniques.',
              'citations': 180,
          },
      ],
      'climate change': [
          {
              'title': 'Climate Models and Predictions',
              'authors': 'Garcia et al.',
              'year': 2023,
              'abstract': 'Improved climate modeling techniques for long-term predictions.',
              'citations': 560,
          },
          {
              'title': 'Renewable Energy Technologies',
              'authors': 'Brown et al.',
              'year': 2024,
              'abstract': 'Survey of emerging renewable energy technologies.',
              'citations': 340,
          },
      ],
  }

  # Find matching papers
  results = []
  query_lower = query.lower()
  for topic, papers in papers_db.items():
    if topic in query_lower or any(
        word in topic for word in query_lower.split()
    ):
      results.extend(papers[:max_results])

  if not results:
    return json.dumps({'message': 'No papers found for this query.'})

  return json.dumps({'papers': results[:max_results]}, indent=2)


def get_citation_count(paper_title: str) -> str:
  """Get the citation count for a specific paper.

  Args:
    paper_title: The title of the paper.

  Returns:
    JSON string with citation information.
  """
  # Simulated citation data
  citations = {
      'Deep Learning for Computer Vision': {
          'count': 450,
          'recent_trend': 'increasing',
          'h_index_contribution': 12,
      },
      'Transformer Architectures in NLP': {
          'count': 890,
          'recent_trend': 'stable',
          'h_index_contribution': 18,
      },
      'Quantum Algorithms for Optimization': {
          'count': 230,
          'recent_trend': 'increasing',
          'h_index_contribution': 8,
      },
  }

  for title, data in citations.items():
    if title.lower() in paper_title.lower():
      return json.dumps(
          {'paper': paper_title, 'citation_data': data}, indent=2
      )

  return json.dumps(
      {'paper': paper_title, 'message': 'Citation data not available.'}
  )


def analyze_research_trends(
    topic: str, time_period: str = 'last_year'
) -> str:
  """Analyze research trends for a given topic.

  Args:
    topic: The research topic to analyze.
    time_period: Time period for analysis (last_year, last_5_years).

  Returns:
    JSON string with trend analysis.
  """
  # Simulated trend data
  trends = {
      'machine learning': {
          'last_year': {
              'growth_rate': '35%',
              'hot_subtopics': [
                  'Large Language Models',
                  'Multimodal Learning',
                  'Efficient Training',
              ],
              'funding_increase': '42%',
              'top_institutions': ['MIT', 'Stanford', 'CMU'],
          },
          'last_5_years': {
              'growth_rate': '180%',
              'hot_subtopics': [
                  'Deep Learning',
                  'Transfer Learning',
                  'Neural Architecture Search',
              ],
              'funding_increase': '220%',
              'top_institutions': ['MIT', 'Stanford', 'Berkeley'],
          },
      },
      'quantum computing': {
          'last_year': {
              'growth_rate': '28%',
              'hot_subtopics': [
                  'Quantum Error Correction',
                  'Quantum Algorithms',
                  'Quantum Hardware',
              ],
              'funding_increase': '55%',
              'top_institutions': ['IBM Research', 'Google Quantum AI', 'MIT'],
          },
      },
  }

  topic_lower = topic.lower()
  for key, data in trends.items():
    if key in topic_lower:
      period_data = data.get(time_period, data.get('last_year'))
      return json.dumps(
          {'topic': topic, 'period': time_period, 'trends': period_data},
          indent=2,
      )

  return json.dumps(
      {'topic': topic, 'message': 'Trend data not available for this topic.'}
  )


def calculate_research_impact(papers: list[dict[str, Any]]) -> str:
  """Calculate the overall research impact from a list of papers.

  Args:
    papers: List of paper dictionaries with citation counts.

  Returns:
    JSON string with impact metrics.
  """
  if not papers:
    return json.dumps({'message': 'No papers provided for analysis.'})

  total_citations = sum(p.get('citations', 0) for p in papers)
  avg_citations = total_citations / len(papers) if papers else 0
  high_impact = [p for p in papers if p.get('citations', 0) > 300]

  impact_score = 'High' if avg_citations > 400 else 'Medium' if avg_citations > 200 else 'Moderate'

  return json.dumps(
      {
          'total_papers': len(papers),
          'total_citations': total_citations,
          'average_citations': round(avg_citations, 1),
          'high_impact_papers': len(high_impact),
          'impact_score': impact_score,
      },
      indent=2,
  )


# Create the agent with PlanReActPlanner
root_agent = Agent(
    model='iflow/qwen3-coder-plus',
    name='research_assistant',
    description='A research assistant that helps analyze academic papers and research trends using structured planning.',
    instruction="""
You are a research assistant that helps users understand academic research topics.

Your capabilities:
- Search for academic papers on various topics
- Analyze citation patterns and research impact
- Identify research trends over time
- Provide comprehensive summaries of research areas

When answering questions:
1. Break down complex queries into clear steps
2. Use available tools to gather information systematically
3. Reason about the information you collect
4. Synthesize findings into a coherent answer

Be thorough but concise. Always cite specific papers when making claims.
    """,
    tools=[
        search_papers,
        get_citation_count,
        analyze_research_trends,
        calculate_research_impact,
    ],
    planner=PlanReActPlanner(),
)
