"""Reusable form components and helpers."""

import streamlit as st
from typing import List, Optional, Tuple, Any


def render_progress_bar(current_step: int, total_steps: int, labels: Optional[List[str]] = None) -> None:
    """
    Render a step progress indicator.
    
    Args:
        current_step: Current step (1-indexed)
        total_steps: Total number of steps
        labels: Optional list of step labels
    """
    progress = current_step / total_steps
    st.progress(progress)
    
    if labels and len(labels) >= total_steps:
        cols = st.columns(total_steps)
        for i, col in enumerate(cols):
            step_num = i + 1
            is_current = step_num == current_step
            is_completed = step_num < current_step
            
            with col:
                if is_completed:
                    st.markdown(f"<div style='text-align: center; color: #66BB6A;'>✓ {labels[i]}</div>", 
                               unsafe_allow_html=True)
                elif is_current:
                    st.markdown(f"<div style='text-align: center; color: #00897B; font-weight: 600;'>{step_num}. {labels[i]}</div>", 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; color: #90A4AE;'>{step_num}. {labels[i]}</div>", 
                               unsafe_allow_html=True)


def text_input_with_validation(
    label: str,
    key: str,
    validator: callable = None,
    placeholder: str = "",
    help_text: str = "",
    password: bool = False
) -> Tuple[str, bool, str]:
    """
    Text input with built-in validation.
    
    Args:
        label: Input label
        key: Streamlit session state key
        validator: Validation function returning (is_valid, message)
        placeholder: Input placeholder
        help_text: Help text to display
        password: Whether to mask input
        
    Returns:
        Tuple of (value, is_valid, validation_message)
    """
    input_type = "password" if password else "default"
    value = st.text_input(
        label,
        key=key,
        placeholder=placeholder,
        help=help_text,
        type=input_type
    )
    
    is_valid = True
    message = ""
    
    if value and validator:
        is_valid, message = validator(value)
        if not is_valid:
            st.error(message)
    
    return value, is_valid, message


def number_input_with_validation(
    label: str,
    key: str,
    min_value: float = 0,
    max_value: float = 100,
    step: float = 1,
    validator: callable = None,
    help_text: str = ""
) -> Tuple[float, bool, str]:
    """
    Number input with built-in validation.
    
    Args:
        label: Input label
        key: Streamlit session state key
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        step: Step increment
        validator: Validation function returning (is_valid, message)
        help_text: Help text to display
        
    Returns:
        Tuple of (value, is_valid, validation_message)
    """
    value = st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        step=step,
        key=key,
        help=help_text
    )
    
    is_valid = True
    message = ""
    
    if validator:
        is_valid, message = validator(value)
        if not is_valid:
            st.error(message)
    
    return value, is_valid, message


def render_questionnaire_question(
    question_num: int,
    question_text: str,
    options: dict,
    key_prefix: str
) -> Optional[int]:
    """
    Render a questionnaire question with radio options.
    
    Args:
        question_num: Question number (for display)
        question_text: The question text
        options: Dict of {value: label} for options
        key_prefix: Prefix for the session state key
        
    Returns:
        Selected option value or None
    """
    st.markdown(f"**{question_num}. {question_text}**")
    
    option_labels = list(options.values())
    option_values = list(options.keys())
    
    selected_label = st.radio(
        "Select one:",
        options=option_labels,
        key=f"{key_prefix}_q{question_num}",
        label_visibility="collapsed",
        horizontal=True
    )
    
    if selected_label:
        selected_index = option_labels.index(selected_label)
        return option_values[selected_index]
    
    return None


def render_slider_with_labels(
    label: str,
    min_value: int,
    max_value: int,
    key: str,
    labels_dict: dict = None,
    default: int = None
) -> int:
    """
    Render a slider with custom value labels.
    
    Args:
        label: Slider label
        min_value: Minimum value
        max_value: Maximum value
        key: Session state key
        labels_dict: Dict mapping values to labels
        default: Default value
        
    Returns:
        Selected value
    """
    value = st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default or min_value,
        key=key
    )
    
    if labels_dict and value in labels_dict:
        st.caption(f"Selected: **{labels_dict[value]}**")
    
    return value


def render_multiselect_chips(
    label: str,
    options: List[str],
    key: str,
    max_selections: int = None
) -> List[str]:
    """
    Render a multiselect with chip-style display.
    
    Args:
        label: Input label
        options: List of available options
        key: Session state key
        max_selections: Maximum number of selections allowed
        
    Returns:
        List of selected options
    """
    selected = st.multiselect(
        label,
        options=options,
        key=key,
        help=f"Select up to {max_selections} options" if max_selections else None
    )
    
    if max_selections and len(selected) > max_selections:
        st.warning(f"Please select at most {max_selections} options")
        selected = selected[:max_selections]
    
    return selected


def render_form_navigation(
    current_step: int,
    total_steps: int,
    on_back: callable = None,
    on_next: callable = None,
    on_submit: callable = None,
    next_disabled: bool = False
) -> None:
    """
    Render form navigation buttons (Back/Next/Submit).
    
    Args:
        current_step: Current step number
        total_steps: Total number of steps
        on_back: Callback for back button
        on_next: Callback for next button
        on_submit: Callback for submit button (on last step)
        next_disabled: Whether next/submit is disabled
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_step > 1 and on_back:
            if st.button("← Back", key="nav_back", use_container_width=True):
                on_back()
    
    with col3:
        if current_step < total_steps:
            if on_next:
                if st.button("Next →", key="nav_next", disabled=next_disabled, use_container_width=True):
                    on_next()
        else:
            if on_submit:
                if st.button("Submit ✓", key="nav_submit", disabled=next_disabled, use_container_width=True):
                    on_submit()
