"""
NLP processing module for extracting micro-statements from legislative bill text.

This module uses spaCy and transformers to:
1. Extract structured statements following: Actor + Action + Target
2. Perform sentiment analysis on extracted statements
3. Extract named entities for better categorization
4. Generate embeddings for similarity comparison
"""

import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class NLPProcessor:
    """
    Main NLP processor for bill text analysis and micro-statement extraction.
    """
    
    def __init__(self):
        """Initialize NLP models lazily to avoid loading at import time."""
        self._nlp = None
        self._sentiment_analyzer = None
        self._embedder = None
    
    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy model: en_core_web_sm")
            except OSError:
                logger.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
                raise
        return self._nlp
    
    @property
    def sentiment_analyzer(self):
        """Lazy load sentiment analysis model."""
        if self._sentiment_analyzer is None:
            try:
                from transformers import pipeline
                self._sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    truncation=True,
                    max_length=512
                )
                logger.info("Loaded sentiment analysis model")
            except Exception as e:
                logger.error(f"Failed to load sentiment analyzer: {e}")
                raise
        return self._sentiment_analyzer
    
    @property
    def embedder(self):
        """Lazy load sentence transformer for embeddings."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.error(f"Failed to load embedder: {e}")
                raise
        return self._embedder
    
    def extract_micro_statements(self, bill_text: str, bill_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Extract micro-statements from bill text.
        
        Args:
            bill_text: The full text of the bill
            bill_metadata: Optional metadata about the bill (jurisdiction, party, etc.)
            
        Returns:
            List of dictionaries containing extracted statements
        """
        if not bill_text or not bill_text.strip():
            return []
        
        statements = []
        
        # Process text with spaCy
        doc = self.nlp(bill_text[:1000000])  # Limit to 1M chars to avoid memory issues
        
        # Extract sentences
        for sent in doc.sents:
            # Skip very short sentences
            if len(sent.text.split()) < 5:
                continue
            
            # Extract subject-verb-object triples
            triples = self._extract_svo_triples(sent)
            
            for triple in triples:
                actor, action, target = triple
                
                # Check if this looks like a policy statement
                if self._is_policy_statement(actor, action, target):
                    statement = self._create_statement(
                        sent, actor, action, target, bill_metadata
                    )
                    statements.append(statement)
        
        return statements
    
    def _extract_svo_triples(self, sentence) -> List[Tuple[str, str, str]]:
        """
        Extract Subject-Verb-Object triples from a sentence.
        
        Args:
            sentence: spaCy Span object
            
        Returns:
            List of (subject, verb, object) tuples
        """
        triples = []
        
        # Find verbs
        for token in sentence:
            if token.pos_ == "VERB":
                # Find subject
                subject = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = self._get_phrase(child)
                        break
                
                # Find object
                obj = None
                for child in token.children:
                    if child.dep_ in ("dobj", "attr", "dative", "pobj"):
                        obj = self._get_phrase(child)
                        break
                
                # Find prepositional objects if no direct object
                if not obj:
                    for child in token.children:
                        if child.dep_ == "prep":
                            for pobj_child in child.children:
                                if pobj_child.dep_ == "pobj":
                                    obj = self._get_phrase(pobj_child)
                                    break
                            if obj:
                                break
                
                if subject and obj:
                    verb_phrase = self._get_verb_phrase(token)
                    triples.append((subject, verb_phrase, obj))
        
        return triples
    
    def _get_phrase(self, token) -> str:
        """Get the full phrase for a token including its children."""
        phrase_tokens = [token]
        
        # Add modifiers
        for child in token.children:
            if child.dep_ in ("det", "amod", "compound", "poss", "nummod", "advmod"):
                phrase_tokens.append(child)
        
        # Sort by position and join
        phrase_tokens.sort(key=lambda t: t.i)
        return " ".join(t.text for t in phrase_tokens)
    
    def _get_verb_phrase(self, verb_token) -> str:
        """Get the full verb phrase including auxiliaries and particles."""
        phrase_tokens = [verb_token]
        
        # Add auxiliaries
        for child in verb_token.children:
            if child.dep_ in ("aux", "auxpass", "neg", "advmod", "prt"):
                phrase_tokens.append(child)
        
        # Sort by position and join
        phrase_tokens.sort(key=lambda t: t.i)
        return " ".join(t.text for t in phrase_tokens)
    
    def _is_policy_statement(self, subject: str, verb: str, obj: str) -> bool:
        """
        Determine if an SVO triple represents a policy statement.
        
        Args:
            subject: The subject phrase
            verb: The verb phrase
            obj: The object phrase
            
        Returns:
            True if this appears to be a policy statement
        """
        # Keywords that indicate political actors
        political_keywords = [
            "legislator", "legislature", "senator", "representative", "congress",
            "assembly", "council", "committee", "department", "agency", "commission",
            "governor", "mayor", "official", "government", "state", "county", "city",
            "board", "authority"
        ]
        
        # Keywords that indicate affected groups
        target_keywords = [
            "citizen", "voter", "resident", "person", "individual", "people",
            "public", "community", "taxpayer", "family", "child", "student",
            "worker", "employee", "business", "organization", "owner"
        ]
        
        # Policy action verbs
        action_verbs = [
            "shall", "must", "require", "prohibit", "allow", "permit", "authorize",
            "establish", "create", "provide", "fund", "allocate", "regulate",
            "enforce", "implement", "amend", "repeal", "adopt", "approve"
        ]
        
        subject_lower = subject.lower()
        verb_lower = verb.lower()
        obj_lower = obj.lower()
        
        # Check if subject contains political keywords
        has_political_subject = any(kw in subject_lower for kw in political_keywords)
        
        # Check if object contains target keywords
        has_target_object = any(kw in obj_lower for kw in target_keywords)
        
        # Check if verb is a policy action
        has_policy_verb = any(v in verb_lower for v in action_verbs)
        
        # Return true if it has characteristics of a policy statement
        return (has_political_subject or has_policy_verb) and len(obj.split()) >= 1
    
    def _create_statement(
        self, 
        sentence, 
        actor: str, 
        action: str, 
        target: str, 
        bill_metadata: Optional[Dict]
    ) -> Dict:
        """
        Create a structured statement dictionary.
        
        Args:
            sentence: The source sentence (spaCy Span)
            actor: The actor/subject
            action: The action/verb
            target: The target/object
            bill_metadata: Optional metadata about the bill
            
        Returns:
            Dictionary containing the statement and metadata
        """
        statement_text = f"{actor} {action} {target}"
        original_text = sentence.text
        
        # Perform sentiment analysis
        sentiment_result = self.analyze_sentiment(statement_text)
        
        # Extract named entities
        entities = self._extract_entities(sentence)
        
        # Determine statement type
        statement_type = self._classify_statement_type(action)
        
        # Build statement dictionary
        statement = {
            'actor': actor,
            'action': action,
            'target': target,
            'statement_text': statement_text,
            'original_text': original_text,
            'statement_type': statement_type,
            'sentiment': sentiment_result['label'],
            'sentiment_score': sentiment_result['score'],
            'entities': entities,
            'extraction_method': 'spacy_svo',
            'confidence_score': self._calculate_confidence(actor, action, target, entities),
        }
        
        # Add bill metadata if available
        if bill_metadata:
            statement.update({
                'session_year': bill_metadata.get('session_year'),
                'jurisdiction': bill_metadata.get('jurisdiction'),
                'district': bill_metadata.get('district'),
                'party': bill_metadata.get('party'),
            })
        
        return statement
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with 'label' (positive/negative/neutral) and 'score'
        """
        if not text or not text.strip():
            return {'label': 'neutral', 'score': 0.0}
        
        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Limit to 512 tokens
            
            # Convert to our sentiment labels
            label = result['label'].lower()
            score = result['score']
            
            # Convert to -1 to 1 scale
            if label == 'negative':
                score = -score
            elif label == 'neutral':
                score = 0.0
            
            # Map to our categories
            if score > 0.3:
                sentiment_label = 'positive'
            elif score < -0.3:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            return {
                'label': sentiment_label,
                'score': score
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'label': 'neutral', 'score': 0.0}
    
    def _extract_entities(self, sentence) -> Dict:
        """
        Extract named entities from a sentence.
        
        Args:
            sentence: spaCy Span object
            
        Returns:
            Dictionary of entity types and their values
        """
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'money': [],
        }
        
        for ent in sentence.ents:
            if ent.label_ == "PERSON":
                entities['people'].append(ent.text)
            elif ent.label_ == "ORG":
                entities['organizations'].append(ent.text)
            elif ent.label_ in ("GPE", "LOC"):
                entities['locations'].append(ent.text)
            elif ent.label_ == "DATE":
                entities['dates'].append(ent.text)
            elif ent.label_ == "MONEY":
                entities['money'].append(ent.text)
        
        return entities
    
    def _classify_statement_type(self, action: str) -> str:
        """
        Classify the type of statement based on the action.
        
        Args:
            action: The action/verb phrase
            
        Returns:
            Statement type: 'action', 'position', or 'impact'
        """
        action_lower = action.lower()
        
        # Action statements (legislative actions)
        action_keywords = [
            "shall", "must", "require", "prohibit", "establish", "create",
            "implement", "enforce", "adopt", "approve", "authorize"
        ]
        
        # Position statements (political positions)
        position_keywords = [
            "believe", "support", "oppose", "favor", "endorse", "advocate"
        ]
        
        # Impact statements (effects on people)
        impact_keywords = [
            "affect", "impact", "benefit", "harm", "help", "protect", "serve"
        ]
        
        if any(kw in action_lower for kw in action_keywords):
            return 'action'
        elif any(kw in action_lower for kw in position_keywords):
            return 'position'
        elif any(kw in action_lower for kw in impact_keywords):
            return 'impact'
        else:
            return 'action'  # Default
    
    def _calculate_confidence(
        self, 
        actor: str, 
        action: str, 
        target: str, 
        entities: Dict
    ) -> float:
        """
        Calculate confidence score for the extraction.
        
        Args:
            actor: The actor phrase
            action: The action phrase
            target: The target phrase
            entities: Extracted entities
            
        Returns:
            Confidence score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Higher confidence if we have named entities
        if entities.get('people') or entities.get('organizations'):
            score += 0.2
        
        # Higher confidence for longer phrases (more context)
        if len(actor.split()) >= 2:
            score += 0.1
        if len(target.split()) >= 2:
            score += 0.1
        
        # Higher confidence if action contains modal verbs
        if any(modal in action.lower() for modal in ['shall', 'must', 'will', 'should']):
            score += 0.1
        
        return min(score, 1.0)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding
        """
        if not text or not text.strip():
            return []
        
        try:
            embedding = self.embedder.encode(text[:512])  # Limit length
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []


# Singleton instance
_processor = None


def get_processor() -> NLPProcessor:
    """Get or create the singleton NLP processor instance."""
    global _processor
    if _processor is None:
        _processor = NLPProcessor()
    return _processor
