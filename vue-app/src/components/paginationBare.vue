<template>
    <ul class="pagination">
        <li class="page-item-clickable" :class="{disabled:currentPage==1}">
            <a class="page-link" @click="onPagerClick('prev')">&laquo;</a></li>
        <li v-for="(item, idx) in pageLinks" v-bind:key="idx" 
            class="page-item-clickable" :class="{disabled:item=='...', active:item==currentPage}"
        >
            <a class="page-link" @click="onPagerClick(item)">[[item]]</a>
        </li>
        <li class="page-item-clickable" :class="{disabled:currentPage==lastPage}">
            <a class="page-link" @click="onPagerClick('next')">&raquo;</a></li>
    </ul>
</template>

<script>
import { ref } from 'vue';
export default {
    name: 'pagination-bare',
    props: ['currentPage', 'totalRows', 'perPage'],
    setup(props, ctx) {
        const lastPage = Math.ceil( props.totalRows / parseInt(props.perPage) )

        var pageLinks = ref([])
        pageLinks.value = getPageLinks(props.currentPage)

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
                newPage = props.currentPage +1
            } else if (data=='prev') {
                newPage = props.currentPage -1
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
    }

}
</script>

<style scoped>
.page-item-clickable {
    @extend .page-item;
    cursor: pointer;
}

li.disabled {
  cursor:auto;
}
li.disabled a {
  pointer-events: none;
}
</style>