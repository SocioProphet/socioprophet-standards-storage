# Graph Query Exemplars v0.1

## 1. Similar case retrieval by symptom + product + fix lineage
```cypher
MATCH (c:Case)-[:HAS_CATEGORY]->(:Category {name:$category})
MATCH (c)-[:RELATES_TO_PRODUCT]->(:Product {id:$product_id})
MATCH (c)-[:HAS_SYMPTOM]->(s:Symptom)
WHERE s.name IN $symptoms
OPTIONAL MATCH (c)-[:RESOLVED_BY]->(r:Resolution)-[:PROMOTED_TO]->(a:Asset)
RETURN c.case_id, collect(DISTINCT s.name) AS matched_symptoms, collect(DISTINCT a.asset_id) AS reusable_assets
ORDER BY size(matched_symptoms) DESC
LIMIT 10;
```

## 2. Route ranking context for confidentiality-sensitive cases
```cypher
MATCH (c:Case {case_id:$case_id})-[:HAS_POLICY_DECISION]->(p:PolicyDecision)
MATCH (c)-[:HAS_CONFIDENCE]->(conf:ConfidenceObject)
MATCH (queue:Queue)
WHERE queue.clearance_level >= coalesce(c.required_clearance, 0)
RETURN queue.queue_id,
       CASE WHEN p.decision_effect = 'escalate' THEN 0.4 ELSE 0 END
       + CASE WHEN conf.confidentiality_risk = 'high' THEN 0.4 ELSE 0 END
       + queue.domain_match_score AS route_score
ORDER BY route_score DESC;
```

## 3. Asset promotion lineage and blast-radius inspection
```cypher
MATCH (a:Asset {asset_id:$asset_id})<-[:USED_ASSET]-(u:AssetUse)<-[:RECORDED_ASSET_USE]-(c:Case)
OPTIONAL MATCH (c)-[:HAS_ROUTE_DECISION]->(r:RouteDecision)
OPTIONAL MATCH (c)-[:HAS_POLICY_DECISION]->(p:PolicyDecision)
RETURN c.case_id, u.usefulness, r.selected_route, p.decision_effect;
```
