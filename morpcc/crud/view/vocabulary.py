import morepath
import html
import deform
from morpfw.crud import permission as crudperms
from ..model import CollectionUI, ModelUI
from ...app import App
from ...root import Root
from ...util import dataclass_to_colander
import rulez


def vocabulary_search(context, request):
    vocab_id = request.GET.get("vocabulary", "").strip()
    if not vocab_id:
        return {}
    term = request.GET.get("term", "").strip()

    vocab = request.app.get_vocabulary(request=request, name=vocab_id)

    result = {"results": []}
    for v in vocab:
        if term:
            if not term.lower() in v["label"].lower():
                continue
        r = {"id": v["value"], "text": v["label"]}
        if v.get('html', None):
            r['html'] = v['html']
        result["results"].append(r)

    return result


@App.json(model=Root, name="vocabulary-search")
def root_vocabulary_search(context, request):
    return vocabulary_search(context, request)
