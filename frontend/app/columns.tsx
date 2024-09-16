"use client"

import { ColumnDef } from "@tanstack/react-table"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
	id: string
	title: string
	status: "idle" | "in contact" | "successful" | "unsuccessful"
	category: string | null
	rating: string | null
	gm_url: string
	website: string | null
	phone: string | null
}

export const columns: ColumnDef<Payment>[] = [
	{
		accessorKey: "title",
		header: "Title",
		cell: ({ row }) => {
			const title = row.getValue("title")
			const url = row.getValue("gm_url")
			console.log(title, url)
	
			return <a className="text-left font-medium" href={`${url}`} target="_blank">{`${title}`}</a>
		},
	},
	{
		accessorKey: "gm_url",
		cell: null,
		header: null
	},
	{
		accessorKey: "id",
		cell: null,
		header: null
	},
	{
		accessorKey: "rating",
		header: "Rating",
	},
	{
		accessorKey: "category",
		header: "Category",
	},
	{
		accessorKey: "status",
		header: "Status",
	},
	{
		accessorKey: "website",
		header: "Website",
		cell: ({ row }) => {
			const url = row.getValue("website")
	
			return <a className="text-left font-medium" href={`${url}`} target="_blank">{`${url}`}</a>
		},
	},
	{
		accessorKey: "phone",
		header: "Phone",
		cell: ({ row }) => {
			const phone = row.getValue("phone")
	
			return <a className="text-left font-medium" href={`tel:${phone}`} target="_blank">{`${phone}`}</a>
		},
	},
]
