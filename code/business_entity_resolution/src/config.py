"""
Configuration parameters for business entity resolution pipeline.

IMPORTANT CONSTRAINTS FROM README:
1. No external data lookup / geocoding APIs (MIT/Apache 2.0 only)
2. Test set contains France (not in training) - do NOT hard-code country labels
3. All files are tab-separated (.tsv) - use sep='\t' when loading
4. Max 8 billion parameters for ML model
5. Precision-heavy F_0.5 metric - penalize false merges heavily

Author: Challenge Participant
License: MIT/Apache 2.0 compliant
"""

import os
from typing import Dict


DATA_CONFIG = {
    'train_dir': '../../dataset_nd_resources/dataset/train',
    'test_dir': '../../dataset_nd_resources/dataset/test',
    'output_dir': '../../output',

    'source1_train': 'train_source1.tsv',
    'source2_train': 'train_source2.tsv',
    'source3_train': 'train_source3.tsv',
    'ground_truth': 'train_ground_truth.tsv',

    'source1_test': 'test_source1.tsv',
    'source2_test': 'test_source2.tsv',
    'source3_test': 'test_source3.tsv',

    # All input files are TSV.
    'separator': '\t',

    'entity_id_prefixes': {
        'S1': 0,
        'S2': 1,
        'S3': 2,
    },

    'validate_before_submit': True,
}


NORMALIZATION_CONFIG = {
    'normalize_whitespace': True,
    'lowercase': True,

    'remove_trailing_punctuation': [
        ',', '.', ';', ':', '?', '!'
    ],

    'ampersand_to_and': True,
    'preserve_internal_periods': False,

    'abbreviation_expansions': {
        'corp': 'corporation',
        'corps': 'corporations',
        'pvt': 'private',
        'ltd': 'limited',
        'inc': 'incorporated',
        'llc': 'limited liability company',
        'llp': 'limited partnership',

        'st': 'street',
        'sts': 'streets',
        'rd': 'road',
        'rds': 'roads',
        'ave': 'avenue',
        'aves': 'avenues',
        'blvd': 'boulevard',
        'blvds': 'boulevards',
        'pl': 'place',
        'pls': 'places',
        'dr': 'drive',
        'drs': 'drives',
        'ln': 'lane',
        'lns': 'lanes',
        'ct': 'court',
        'cts': 'courts',
        'way': 'way',

        'ny': 'new york',
        'ca': 'california',
        'tx': 'texas',
        'il': 'illinois',
    },

    'unicode_normalization': 'NFKC',
    'strip_accents': False,
    'keep_original_value': True,
}


FEATURE_CONFIG = {
    'tfidf_min_df': 2,
    'tfidf_max_df': 1.0,
    'tfidf_ngram_range': (1, 2),

    'char_tfidf_ngram_range': (2, 5),
    'char_tfidf_min_df': 2,
    'char_tfidf_max_features': 100_000,

    'jaccard_threshold': 0.5,

    'levenshtein_distance_cutoff': 3,
    'levenshtein_ratio_threshold': 0.8,

    'stopwords': [
        'the', 'at', 'near', 'of', 'in', 'on', 'for', 'with',
        'by', 'to', 'from', 'and', 'or', 'is', 'are', 'was', 'were'
    ],

    # Do not add test-only countries here.
    'known_training_countries': ['US', 'India'],
    'unseen_country_handling': 'onehot_ignore_unseen',

    'country_case_sensitive': False,
    'country_unknown_token': '__UNKNOWN__',

    'include_exact_match_features': True,
    'include_length_features': True,
    'include_token_count_features': True,

    'field_weights': {
        'name': 1.00,
        'address': 0.90,
        'city': 0.75,
        'state': 0.70,
        'postal_code': 0.85,
        'country': 0.50,
        'phone': 0.95,
        'email': 1.00,
    },
}


BLOCKING_CONFIG = {
    'enabled': True,

    'max_candidates_per_record': 200,
    'max_block_size': 5_000,

    'strategies': [
        'exact_normalized_name',
        'name_prefix',
        'postal_code',
        'phone_suffix',
        'email_domain',
        'city_name',
        'address_tokens',
    ],

    'name_prefix_length': 4,
    'city_prefix_length': 4,
    'phone_suffix_length': 7,
    'address_token_min_length': 4,
    'max_token_frequency_ratio': 0.10,
}


MATCHING_CONFIG = {
    'match_probability_threshold': 0.90,
    'high_confidence_threshold': 0.97,
    'non_match_probability_threshold': 0.10,

    'minimum_best_candidate_margin': 0.10,
    'ambiguous_margin': 0.05,

    'require_supporting_evidence': True,
    'minimum_strong_fields_for_match': 1,

    'strong_fields': [
        'email',
        'phone',
        'postal_code',
    ],

    'reject_conflicting_email': True,
    'reject_conflicting_phone': True,

    # Country mismatches are not automatically treated as contradictions.
    'reject_country_mismatch': False,

    'allow_multiple_source_records_per_entity': True,
    'unique_assignment_per_source_record': True,
}


MODEL_CONFIG = {
    'model_type': 'hist_gradient_boosting',

    'learning_rate': 0.05,
    'max_iter': 300,
    'max_leaf_nodes': 31,
    'max_depth': None,
    'min_samples_leaf': 20,
    'l2_regularization': 1.0,

    'early_stopping': True,
    'validation_fraction': 0.15,
    'n_iter_no_change': 25,
    'tol': 1e-7,

    'random_state': 42,

    # Challenge limit.
    'max_parameters': 8_000_000_000,
}


TRAINING_CONFIG = {
    'random_state': 42,
    'validation_size': 0.20,
    'stratify': True,

    'handle_class_imbalance': True,
    'class_weight': 'balanced',

    'generate_negative_pairs': True,
    'negative_to_positive_ratio': 3.0,

    'prevent_entity_leakage': True,

    'use_cross_validation': True,
    'cv_folds': 5,
}


EVALUATION_CONFIG = {
    'primary_metric': 'f0.5',
    'f_beta': 0.5,

    'metrics': [
        'precision',
        'recall',
        'f0.5',
        'f1',
        'accuracy',
    ],

    'optimize_threshold': True,

    'threshold_min': 0.50,
    'threshold_max': 0.995,
    'threshold_step': 0.005,

    'minimum_precision_target': 0.95,
    'prefer_precision_on_tie': True,
    'tie_tolerance': 0.001,
}


OUTPUT_CONFIG = {
    'output_dir': DATA_CONFIG['output_dir'],

    'predictions_file': 'predictions.tsv',
    'submission_file': 'submission.tsv',

    'evaluation_file': 'evaluation_metrics.json',
    'threshold_file': 'optimal_threshold.json',

    'save_candidate_pairs': False,
    'candidate_pairs_file': 'candidate_pairs.tsv',

    'save_model': True,
    'model_file': 'entity_resolution_model.joblib',

    'save_feature_metadata': True,
    'feature_metadata_file': 'feature_metadata.json',

    'create_output_dir': True,
}


LOGGING_CONFIG = {
    'level': 'INFO',
    'show_progress': True,

    'show_match_examples': True,
    'num_match_examples': 10,

    'show_ambiguous_examples': True,
    'num_ambiguous_examples': 10,

    'show_rejected_examples': False,
    'num_rejected_examples': 10,
}


RANDOM_SEED = 42


def get_train_path(filename: str) -> str:
    return os.path.join(DATA_CONFIG['train_dir'], filename)


def get_test_path(filename: str) -> str:
    return os.path.join(DATA_CONFIG['test_dir'], filename)


def get_output_path(filename: str) -> str:
    return os.path.join(DATA_CONFIG['output_dir'], filename)


def get_train_files() -> Dict[str, str]:
    return {
        'source1': get_train_path(DATA_CONFIG['source1_train']),
        'source2': get_train_path(DATA_CONFIG['source2_train']),
        'source3': get_train_path(DATA_CONFIG['source3_train']),
        'ground_truth': get_train_path(DATA_CONFIG['ground_truth']),
    }


def get_test_files() -> Dict[str, str]:
    return {
        'source1': get_test_path(DATA_CONFIG['source1_test']),
        'source2': get_test_path(DATA_CONFIG['source2_test']),
        'source3': get_test_path(DATA_CONFIG['source3_test']),
    }


def ensure_output_directory() -> None:
    if OUTPUT_CONFIG['create_output_dir']:
        os.makedirs(DATA_CONFIG['output_dir'], exist_ok=True)


def validate_config() -> None:
    if DATA_CONFIG['separator'] != '\t':
        raise ValueError(
            "Dataset separator must be '\\t' because input files are TSV."
        )

    if MODEL_CONFIG['max_parameters'] > 8_000_000_000:
        raise ValueError(
            "Configured model exceeds the 8 billion parameter limit."
        )

    if EVALUATION_CONFIG['primary_metric'].lower() != 'f0.5':
        raise ValueError("Primary evaluation metric must be F0.5.")

    if EVALUATION_CONFIG['f_beta'] != 0.5:
        raise ValueError("F-beta value must be 0.5.")

    if FEATURE_CONFIG['unseen_country_handling'] != 'onehot_ignore_unseen':
        raise ValueError(
            "Unseen countries must be handled generically."
        )

    threshold_min = EVALUATION_CONFIG['threshold_min']
    threshold_max = EVALUATION_CONFIG['threshold_max']

    if not 0.0 <= threshold_min <= 1.0:
        raise ValueError("threshold_min must be between 0 and 1.")

    if not 0.0 <= threshold_max <= 1.0:
        raise ValueError("threshold_max must be between 0 and 1.")

    if threshold_min >= threshold_max:
        raise ValueError(
            "threshold_min must be smaller than threshold_max."
        )

    if BLOCKING_CONFIG['max_candidates_per_record'] <= 0:
        raise ValueError(
            "max_candidates_per_record must be positive."
        )

    if BLOCKING_CONFIG['max_block_size'] <= 0:
        raise ValueError(
            "max_block_size must be positive."
        )


if __name__ == '__main__':
    validate_config()
    ensure_output_directory()
    print("Configuration validation passed.")