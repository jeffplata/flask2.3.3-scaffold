export default function useTable(ctx, fields, sortBy, sortDesc) {
    
        const fields_simple = fields.value.map(function(n) {
            if (typeof n==='string') {
                return n
            } else {
                return n.key
            }
        })

        function onClickSortBadge() {
            ctx.emit('changeSortBy', '', '')
        }

        function onHeaderClick(fld) {
            if (typeof fld==='string') {
                ctx.emit('changeSortBy', '', '')
            } else {
                if (fld.key == sortBy) {
                    ctx.emit('changeSortBy', fld.key, !sortDesc)    
                } else {
                    ctx.emit('changeSortBy', fld.key, false)
                }
            }
        }

        function onRowClick(rowData, idx) {
            ctx.emit('rowClick', rowData, idx)
        }

    return {
        onHeaderClick, onRowClick, fields_simple,
        onClickSortBadge,
    }
}