MODEL_TYPES = [
    # zeroshot models
    "zeroshot_regular", "zeroshot_sentence", "zeroshot_chunked", "zeroshot_child_labels",
    # embedding models
    "embedding_child_labels", "embedding_regular", "embedding_sentence", "embedding_chunked", "embedding_ground_up", "embedding_ground_up_greedy",
    # supervised models
    "huggingface_model",
    # hybrid models
    "hybrid_base_model", "hybrid_selective_model"
]

DATASET_TYPES = [
    # return pulled dataset
    "mirror",
    # single label dataset0
    "s1_general",
    # multilabel dataset
    "m2_general", "m1_general", "m1_article", "m1_article_split", "m1_description", "m1_motivation", "m1_shorttitle",
    # dynamic dataset for node based selection
    "dynamic_general",
    # summary statistics dataset
    "summary_stat_dataset"
]

TAXONOMY_URIS = [
    "http://stad.gent/id/concepts/gent_words",
    "http://stad.gent/id/concepts/policy_domains_themes",
    "http://stad.gent/id/concepts/business_capabilities"
]

EMBEDDING_MODELS = [
    "paraphrase-multilingual-mpnet-base-v2",
    "intfloat/multilingual-e5-small",
    "thenlper/gte-large",
    "multi-qa-mpnet-base-dot-v1"
]

ZEROSHOT_MODELS = [
    "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
    "facebook/bart-large-mnli",
    "mjwong/multilingual-e5-base-xnli-anli",
    "joeddav/xlm-roberta-large-xnli"
]

TRAIN_FLAVOURS =[
    "bert", "setfit", "distilbert"
]

INFERENCE_CONFIG_EXAMPLE: dict[str, Any] = {"flavour": "huggingface_model", "model_id": "mlflow:/bert__business_capabilities__parent_node", "stage": "Production", "sub_nodes": [{"flavour": "huggingface_model", "model_id": "mlflow:/bert__business_capabilities__ondersteunende_capabilities", "stage": "Production", "sub_nodes": [], "uri": "http://stad.gent/id/concepts/business_capabilities/concept_90"}, {"flavour": "huggingface_model", "model_id": "mlflow:/bert__business_capabilities__sturende_capabilities", "stage": "Production", "sub_nodes": [], "uri": "http://stad.gent/id/concepts/business_capabilities/concept_1"}, {"flavour": "huggingface_model", "model_id": "mlflow:/bert__business_capabilities__uitvoerende_capabilities", "stage": "Production", "sub_nodes": [], "uri": "http://stad.gent/id/concepts/business_capabilities/concept_13"}], "uri": "http://stad.gent/id/concepts/business_capabilities"}

TOPIC_MODELS = ["topic_model_regular", "topic_model_hierarchic", "topic_model_dynamic"]