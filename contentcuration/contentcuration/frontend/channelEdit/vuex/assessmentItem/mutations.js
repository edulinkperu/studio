import Vue from 'vue';
import { mergeMapItem } from 'shared/vuex/utils';
import { applyMods } from 'shared/data/applyRemoteChanges';

export function UPDATE_ASSESSMENTITEM(state, assessmentItem) {
  if (!assessmentItem.assessment_id) {
    throw ReferenceError('assessment_id must be defined to update an assessment item');
  }
  if (!assessmentItem.contentnode) {
    throw ReferenceError('contentnode must be defined to update an assessment item');
  }

  // data can come from API that returns answers and hints as string
  let answers, hints;
  if (typeof assessmentItem.answers === 'string') {
    answers = JSON.parse(assessmentItem.answers);
  } else {
    answers = assessmentItem.answers ? assessmentItem.answers : null;
  }

  if (answers) {
    answers.sort((answer1, answer2) => (answer1.order > answer2.order ? 1 : -1));
    assessmentItem.answers = answers;
  }

  if (typeof assessmentItem.hints === 'string') {
    hints = JSON.parse(assessmentItem.hints);
  } else {
    hints = assessmentItem.hints ? assessmentItem.hints : null;
  }

  if (hints) {
    hints.sort((hint1, hint2) => (hint1.order > hint2.order ? 1 : -1));
    assessmentItem.hints = hints;
  }

  Vue.set(
    state.assessmentItemsMap,
    assessmentItem.contentnode,
    mergeMapItem(
      state.assessmentItemsMap[assessmentItem.contentnode] || {},
      assessmentItem,
      'assessment_id'
    )
  );
}

export function UPDATE_ASSESSMENTITEM_FROM_INDEXEDDB(state, { id, ...mods }) {
  if (id && state.assessmentItemsMap[id]) {
    applyMods(state.assessmentItemsMap[id], mods);
  }
}

export function DELETE_ASSESSMENTITEM(state, assessmentItem) {
  Vue.delete(state.assessmentItemsMap[assessmentItem.contentnode], assessmentItem.assessment_id);
}
