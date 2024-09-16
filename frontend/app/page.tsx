import { Payment, columns } from "./columns"
import { DataTable } from "./data-table"
 

async function getData(): Promise<Payment[]> {
	const data = await fetch("http://127.0.0.1:5000/leads", {cache: "no-store"})
	const leads = (await data.json()).map((lead) => {
		return {
			id : lead.id,
			title: lead.title,
			rating: lead.rating && `${lead.rating.stars} ( ${lead.rating.amount} )`,
			gm_url: lead.gm_url,
			category: lead.category,
			website: lead.website,
			phone: lead.phone,
			status: lead.status
		}
	})
	return leads
  }

export default async function Home() {
	const data = await getData()
	return (
		<div className="min-h-screen">
			<main className="shadow-[inset_0_-2px_0_rgba(20,20,20,1)] h-full">
				<DataTable columns={columns} data={data}></DataTable>
			</main>
		</div>
  	);
}
