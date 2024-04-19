const templateCache = `
    <ul class="pagination">
    <li class="page-item page-item-clickable" :class="{disabled:currentPage==1}">
        <a class="page-link" @click="onPagerClick('prev')">&laquo;</a></li>
    <li v-for="(item, idx) in pageLinks" v-bind:key="idx" 
        class="page-item page-item-clickable" :class="{disabled:item=='...', active:item==currentPage}"
    >
        <a class="page-link" @click="onPagerClick(item)">[[item]]</a>
    </li>
    <li class="page-item page-item-clickable" :class="{disabled:currentPage==lastPage}">
        <a class="page-link" @click="onPagerClick('next')">&raquo;</a></li>
    </ul>
    `

const styles = `
    .page-item-clickable {
        cursor: pointer;
    }

    li.disabled {
        cursor:auto;
    }
    li.disabled a {
        pointer-events: none;
    }
`
// Function to add styles to the head of the document
const addStyles = (styles) => {
    const styleElement = document.createElement('style');
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
};

addStyles(styles); // Adding styles to the head

const { ref, toRefs } = Vue;

const VuePagination = {
    props: ['currentPage', 'totalRows', 'perPage'],
    setup(props, ctx) {
        const { currentPage, totalRows, perPage } = toRefs(props)
        const lastPage = Math.ceil( totalRows.value / parseInt(perPage.value) )

        const pageLinks = ref([])
        pageLinks.value = getPageLinks(currentPage.value)

        function getPageLinks(curPage) {
            let pageLinks = []
            if (lastPage < 8) {
                pageLinks = Array(lastPage).fill(0).map((x, i) => i + 1)
            } else if (curPage < 5) {
                pageLinks = [1, 2, 3, 4, 5, '...', lastPage]
            } else if ((curPage > (lastPage - 4))) {
                pageLinks = [1, '...', lastPage-4, lastPage-3, lastPage-2, lastPage-1, lastPage]
            } else {
                pageLinks = [1, '...', curPage-1, curPage, curPage+1, '...', lastPage]
            }
            return pageLinks
        }
            
        function onPagerClick(data) {
            let newPage
            if (data=='next') {
                newPage = currentPage.value +1
            } else if (data=='prev') {
                newPage = currentPage.value -1
            } else {
                newPage = data
            }
            ctx.emit('pageChanged', newPage)
            pageLinks.value = getPageLinks(newPage)
        }

        return {
            lastPage, pageLinks,
            onPagerClick,
        }
    },
    delimiters: ['[[',']]'],
    template: templateCache,
}

export default VuePagination